from gesture import GestureExtractor

extractor = GestureExtractor(n_points=100, n_fft=21)

while True:
    data = extractor.get()
    print data

