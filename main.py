from scraping import link_definition, table_formation, saving_to_file


def main():
    link_definition()
    df = table_formation()
    saving_to_file(df)


if __name__ == "__main__":
    main()