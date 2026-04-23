import matplotlib.pyplot as plt


def fifo(pages, capacity):
    memory = []
    faults = 0

    print("\n===== FIFO Simulation =====")

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
            print(f"{page} -> {memory} (Fault)")
        else:
            print(f"{page} -> {memory} (Hit)")

    return faults


def lru(pages, capacity):
    memory = []
    faults = 0

    print("\n===== LRU Simulation =====")

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
            print(f"{page} -> {memory} (Fault)")
        else:
            memory.remove(page)
            memory.append(page)
            print(f"{page} -> {memory} (Hit)")

    return faults


def lfu(pages, capacity):
    memory = []
    freq = {}
    faults = 0

    print("\n===== LFU Simulation =====")

    for page in pages:
        if page not in memory:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                lfu_page = min(memory, key=lambda x: freq.get(x, 0))
                memory.remove(lfu_page)
                memory.append(page)
            print(f"{page} -> {memory} (Fault)")
        else:
            print(f"{page} -> {memory} (Hit)")

        freq[page] = freq.get(page, 0) + 1

    return faults


def optimal(pages, capacity):
    memory = []
    faults = 0

    print("\n===== Optimal Simulation =====")

    for i in range(len(pages)):
        page = pages[i]

        if page not in memory:
            faults += 1

            if len(memory) < capacity:
                memory.append(page)
            else:
                future = pages[i + 1:]
                index = []

                for m in memory:
                    if m in future:
                        index.append(future.index(m))
                    else:
                        index.append(float('inf'))

                replace_index = index.index(max(index))
                memory[replace_index] = page

            print(f"{page} -> {memory} (Fault)")
        else:
            print(f"{page} -> {memory} (Hit)")

    return faults


def print_results(name, faults, total):
    hits = total - faults
    ratio = hits / total
    print(f"{name} -> Faults: {faults}, Hits: {hits}, Hit Ratio: {ratio:.2f}")


# ✅ NEW: Graph Function
def show_graph(fifo_f, lru_f, lfu_f, opt_f):
    algorithms = ['FIFO', 'LRU', 'LFU', 'Optimal']
    faults = [fifo_f, lru_f, lfu_f, opt_f]

    plt.bar(algorithms, faults)
    plt.title("Page Replacement Algorithm Comparison")
    plt.xlabel("Algorithms")
    plt.ylabel("Page Faults")
    plt.show()


def main():
    try:
        pages = list(map(int, input("Enter page reference string (space separated): ").split()))
        capacity = int(input("Enter number of frames: "))

        total = len(pages)

        fifo_faults = fifo(pages, capacity)
        lru_faults = lru(pages, capacity)
        lfu_faults = lfu(pages, capacity)
        opt_faults = optimal(pages, capacity)

        print("\n===== FINAL RESULTS =====")
        print_results("FIFO", fifo_faults, total)
        print_results("LRU", lru_faults, total)
        print_results("LFU", lfu_faults, total)
        print_results("Optimal", opt_faults, total)

        # ✅ Show graph
        show_graph(fifo_faults, lru_faults, lfu_faults, opt_faults)

    except:
        print("❌ Invalid input! Please enter numbers only.")


if __name__ == "__main__":
    main()