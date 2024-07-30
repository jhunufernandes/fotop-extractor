from fotop_extractor import FotopExtractor, FotopExtractorSchema


input = FotopExtractorSchema(event_id=90952, runner_id=5637, columns=4)


def main():
    extractor = FotopExtractor(input)
    extractor.run()


if __name__ == "__main__":
    main()
