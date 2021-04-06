def greedy(instance):
    import operator
    requests = sorted(requests, key=operator.attrgetter('firstDay'))