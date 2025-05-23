txt = "duvynqusemrvwdhblgbrzgsqkkcliakffoxxhwowdbtbhdrgdbxssbfkgmygkahwtsaxkbxfimkopcpkyzexvsrrdvsclokcgswhnrvxtvtsbbduqcbdnpvhgftohzyidhmbqwnxvgkmofimnbrpixfrrsgdvqolysakkkahmhxspsvdovotuvrqvyqickodyskoffymrfosevnrnikgmogmrfemsgvooonpcasqhogwrwctqrw"

g1 = []
g1single = []
g2 = []
g2single = []
g3 = []
g3single = []
g4 = []
g4single = []
g5 = []
g5single = []

count = 1
for i in txt:
    if count == 1:
        g1.append(i)
        count += 1

        if i not in g1single:
            g1single.append(i)
    elif count == 2:
        g2.append(i)
        count += 1

        if i not in g2single:
            g2single.append(i)
    elif count == 3:
        g3.append(i)
        count += 1

        if i not in g3single:
            g3single.append(i)
    elif count == 4:
        g4.append(i)
        count += 1

        if i not in g4single:
            g4single.append(i)
    elif count == 5:
        g5.append(i)
        count = 1

        if i not in g5single:
            g5single.append(i)

print(f"g1: {''.join(g1)}")
print("".join(g1single).upper())
print(f"g2: {''.join(g2)}")
print("".join(g2single).upper())
print(f"g3: {''.join(g3)}")
print("".join(g3single).upper())
print(f"g4: {''.join(g4)}")
print("".join(g4single).upper())
print(f"g5: {''.join(g5)}")
print("".join(g5single).upper())