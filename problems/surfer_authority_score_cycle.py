import enum
import random
import pprint

from collections import defaultdict


class Page(enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'


transition_graph = {
    Page.A: [Page.B],
    Page.B: [Page.E],
    Page.E: [Page.A],
    Page.D: [Page.A],
    Page.C: [Page.A],
}


def compute_surfer_authority_score(num_of_simulations):
    surfer_authority_score = defaultdict(int)
    pages = list(Page)

    current_page = random.choice(pages)
    for _ in range(num_of_simulations):
        dice = random.random()
        if 0 <= dice <= 0.85:
            next_page = random.choice(transition_graph[current_page])
        else:
            next_page = random.choice(list(set(pages) - {current_page}))
        surfer_authority_score[next_page] += 1
        current_page = next_page

    surfer_authority_score_percentage = {}
    for p in pages:
        surfer_authority_score_percentage[p] = (
            f'{(surfer_authority_score[p] * 100) / num_of_simulations}%'
        )

    pprint.pprint(surfer_authority_score_percentage, indent=4)


compute_surfer_authority_score(1000 * 1000)





