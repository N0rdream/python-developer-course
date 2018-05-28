#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertoolsю
# Можно свободно определять свои функции и т.п.
# -----------------

from collections import Counter
from itertools import combinations, product, chain


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def assign_ranks():
    return {v: i for i, v in enumerate('123456789TJQKA?')}


def get_rank(card):
    ranks = assign_ranks()
    return ranks[card[-2]]


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    return sorted(get_rank(card) for card in hand)


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    return len(set(card[-1] for card in hand)) == 1


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return len(set(ranks)) == len(ranks) and ranks[-1] - ranks[0] == 4


def count_ranks(n, ranks):
    return [k for k, v in Counter(ranks).items() if v == n]


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    result = count_ranks(n, ranks)
    if result:
        return min(result)


def two_pair(ranks):
    """Если есть две пары, то возврщает два соответствующих ранга,
    иначе возвращает None"""
    result = count_ranks(2, ranks)
    if len(result) == 2:
        return result


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт """
    combs = combinations(hand, 5)
    best_comb = sorted(combs, key=lambda hand: hand_rank(hand))[-1]
    return sorted(best_comb)


def get_jokers(hand):
    return [card for card in hand if card[0] == '?']


def generate_cards(suits):
    return [r + s for r in '123456789TJQKA' for s in suits]


def replace_joker(joker):
    if joker[-1] == 'B':
        return generate_cards('CS')
    return generate_cards('DH')


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    jokers = get_jokers(hand)
    if not jokers:
        return best_hand(hand)
    hand = [c for c in hand if c not in jokers]
    iters = [replace_joker(j) for j in jokers]
    new_hands = [hand + list(comb) for comb in product(*iters)]
    all_combs = chain.from_iterable(combinations(h, 5) for h in new_hands)
    best_comb = sorted(all_combs, key=lambda hand: hand_rank(hand))[-1]
    return sorted(best_comb)
        

def test_best_hand():
    print("test_best_hand...")
    assert (sorted(best_hand("6C 7C 8C 9C TC 5C JS".split()))
            == ['6C', '7C', '8C', '9C', 'TC'])
    assert (sorted(best_hand("TD TC TH 7C 7D 8C 8S".split()))
            == ['8C', '8S', 'TC', 'TD', 'TH'])
    assert (sorted(best_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert (sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split()))
            == ['7C', '8C', '9C', 'JC', 'TC'])
    assert (sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split()))
            == ['7C', 'TC', 'TD', 'TH', 'TS'])
    assert (sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split()))
            == ['7C', '7D', '7H', '7S', 'JD'])
    print('OK')

if __name__ == '__main__':
    test_best_hand()
    test_best_wild_hand()
    


































