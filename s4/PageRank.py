import time

MAX_ITERATIONS = 10
DAMPING_FACTOR = L = 0.85
CONVERGENCE_THRESHOLD = 1e-7


class Airport:
    def __init__ (self, code, name, position):
        self.code = code
        self.name = name
        self.edges = {}
        self.out_weight = 0
        self.position = position
        self.pagerank = -1

    def __repr__(self):
        return f"{self.code} - {self.name.ljust(50, '·')} {self.pagerank} - {self.edges}"


airport_list = []
airport_hash = dict()

first_dangling_airport_index = -1
m = amount_of_dangling_airports = 0

n = -1


def read_airports(fd):
    global n
    print(f"Reading Airport file from {fd}")
    with open(fd, "r", encoding='utf-8') as airports_txt:
        airports = airports_txt.readlines()

    pos = 0
    for line in airports:
        terms = line.split(',')
        if len(terms[4]) == 5:
            airport_code = terms[4].strip('"')
            if airport_code not in airport_hash:
                airport_name = terms[1].strip('"')
                a = Airport(airport_code, airport_name, pos)
                airport_list.append(a)
                airport_hash[airport_code] = a
                pos += 1

    n = len(airport_list)

    for airport in airport_list:
        airport.pagerank = 1/n

    print(f"{n} airports with a valid IATA code found")


def read_routes(fd):
    print(f"Reading Routes file from {fd}")

    with open(fd, 'r', encoding='utf-8') as routes_txt:
        routes = routes_txt.readlines()

    count = 0
    for line in routes:
        terms = line.split(',')
        origin_airport_code = terms[2]
        destination_airport_code = terms[4]
        try:
            origin_airport = airport_hash[origin_airport_code]
            destination_airport = airport_hash[destination_airport_code]
            destination_airport.edges[origin_airport.position] = destination_airport.edges.get(origin_airport.position, 0) + 1
            origin_airport.out_weight += 1
            count += 1
        except KeyError:
            pass

    global first_dangling_airport_index, m
    for i in range(n):
        if airport_list[i].out_weight == 0:
            m += 1
            if first_dangling_airport_index == -1:
                first_dangling_airport_index = i

    print(f"{count} valid routes found")
    print(f"{m} dangling airports with no outgoing flights")


def compute_page_ranks():
    teleport_factor = (1 - L)/n
    P = [1/n] * n
    iterations_done = MAX_ITERATIONS
    for iteration in range(MAX_ITERATIONS):
        Q = [0] * n
        dangling_weight = m * P[first_dangling_airport_index] / n
        for i in range(n):
            airport = airport_list[i]
            summ = 0
            for adj_pos, w in airport.edges.items():
                adjacent_airport = airport_list[adj_pos]
                summ += (P[i] * w) / adjacent_airport.out_weight
            Q[i] = L * (summ + dangling_weight) + teleport_factor
        if have_converged(P, Q):
            iterations_done = iteration + 1
            break
        P = Q

    for i in range(n):
        airport_list[i].pagerank = P[i]
    return iterations_done


def have_converged(p, q):
    for x, y in zip(p, q):
        if abs(x - y) > CONVERGENCE_THRESHOLD:
            return False
    return True


def output_page_ranks():
    airport_list.sort(reverse=True, key=lambda x: x.pagerank)

    with open('output.txt', 'w', encoding='utf-8') as output:
        for i, airport in enumerate(airport_list):
            airport_line = f'{i}:'.ljust(3) + ' ' + str(airport)
            print(airport_line)
            output.write(airport_line + '\n')
        print(f'\n{"-" * 50}\n')


def check_p_sum():
    pagerank_sum = 0
    for airport in airport_list:
        pagerank_sum += airport.pagerank
    assert abs(pagerank_sum - 1) < 10e-10, f'Sum of pageranks is {pagerank_sum} instead of 1'


if __name__ == "__main__":
    read_airports("airports.txt")
    read_routes("routes.txt")
    check_p_sum()
    time1 = time.time()
    iterations = compute_page_ranks()
    check_p_sum()
    time2 = time.time()
    output_page_ranks()
    print("Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)
