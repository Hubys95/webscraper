import csv
import requests
import bs4


def main():
    print("Welcome to my app.")
    print("=" * 40)
    web_page = input("Please insert a page.:")
    filename = input("Please insert a file name.:")

    if web_page.startswith("https://volby.cz/pls/ps2017nss/"):
        html_text = page(web_page)
        districts_from_tables = get_tables(html_text)
        dicts = {}
        new_list = []

        for row in districts_from_tables:
            dict0 = get_info_table(row)
            dicts.update(dict0)

            if dict0 != {'Code': '-', 'Location': '-'}:
                new_url = adress(code_district(row), web_page)
                new_html_text = page(new_url)
                new_first_table = first_table(new_html_text)
                new_next_tables = next_tables(new_html_text)
                for row1 in new_first_table:
                    dict1 = info_first_table(row1)
                    dicts.update(dict1)
                for row2 in new_next_tables:
                    dict2 = info_next_tables(row2)
                    dicts.update(dict2)

                new_list.append(dict(dicts))
                write_data(filename + ".csv", new_list)

            print("Saving...")
        print("Data saved to:", filename)
    else:
        print("Invalid url.")


def page(url: str) -> bs4.BeautifulSoup:
    r = requests.get(url)
    if r.status_code != 200:
        print("Invalid url.")
    html = r.text
    return bs4.BeautifulSoup(html, "html.parser")


def get_tables(html: bs4.BeautifulSoup) -> list:
    district = []
    tables = html.find_all("table", {"class": "table"})
    for table in tables:
        district.extend(table.find_all("tr")[2:])
    return district


def get_info_table(tr) -> dict:
    return {
        "Code": tr.find_all("td")[0].text,
        "Location": tr.find_all("td")[1].text,
    }


def code_district(tr) -> str:
    return tr.find_all("td")[0].text


def first_table(html: bs4.BeautifulSoup) -> list:
    table = html.find(id="ps311_t1")
    return table.find_all("tr")[2:]


def info_first_table(tr) -> dict:
    return {
        "Registered": tr.find_all("td")[3].text.replace("\xa0", "."),
        "Envelopes": tr.find_all("td")[4].text.replace("\xa0", "."),
        "Valid": tr.find_all("td")[7].text.replace("\xa0", "."),
    }


def next_tables(html: bs4.BeautifulSoup) -> list:
    list_ = []
    tables = html.find_all("div", class_="t2_470")

    for table in tables:
        list_.extend(table.find_all("tr")[2:])
    return list_


def info_next_tables(tr) -> dict:
    tables = {tr.find_all("td")[1].text: tr.find_all("td")[2].text.replace(" ", ".")}
    return tables


def adress(number, url):
    return f"https://volby.cz/pls/ps2017nss/ps311?xjazyk" \
           f"=CZ&xkraj=13&xobec={number}&xvyber={url[-4:]}"


def write_data(filename_csv: str, data: list):
    fieldnames = data[0].keys()
    with open(filename_csv, 'w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames, delimiter=',')
        writer.writeheader()
        for row_dict in data:
            writer.writerow(row_dict)
    return writer


main()
