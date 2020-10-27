from urllib.request import urlopen
import json

regions_mapping = {}
regions_mapping["CZ010"] = "Hlavní město Praha"
regions_mapping["CZ020"] = "Středočeský kraj"
regions_mapping["CZ031"] = "Jihočeský kraj"
regions_mapping["CZ032"] = "Plzeňský kraj"
regions_mapping["CZ041"] = "Karlovarský kraj"
regions_mapping["CZ042"] = "Ústecký kraj"
regions_mapping["CZ051"] = "Liberecký kraj"
regions_mapping["CZ052"] = "Královéhradecký kraj"
regions_mapping["CZ053"] = "Pardubický kraj"
regions_mapping["CZ063"] = "Kraj Vysočina"
regions_mapping["CZ064"] = "Jihomoravský kraj"
regions_mapping["CZ071"] = "Olomoucký kraj"
regions_mapping["CZ072"] = "Zlínský kraj"
regions_mapping["CZ080"] = "Moravskoslezský kraj"

def url_to_bulk_file(url, filename, index, type, decode_regions=False, max_docs_per_file=30000):
    """
    Download some json from 'onemocneni-aktualne.mzcr.cz' and save to file
    in bulk elasticsearch format.
    (https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html)

    :param url: source json url
    :param filename: destination file
    :param index: elasticsearch index name
    :param type: elasticsearch type name
    :param max_docs_per_file: maximal number of documents in one file
    """
    data = json.load(urlopen(url))
    file = open(filename, 'w')

    docs = 0
    extra_file_num = 1
    for document in data['data']:
        # create a new file if needed
        if docs > max_docs_per_file:
            file.close()
            dot_pos = filename.find('.')
            file = open(filename[:dot_pos] + '-' + str(extra_file_num) + filename[dot_pos:], 'w')
            extra_file_num += 1
            docs = 0

        # write "action_and_meta_data\n"
        file.write('{"index": {"_index": "' + index + '", "_type": "' + type + '"}}\n')

        # write "optional_source\n"
        if 'okres_lau_kod' in document:
            # reformat region code
            code = document['okres_lau_kod']
            document['okres_lau_kod'] = code[:2] + '-' + code[3:] # e.g. "CZ0803" -> "CZ-803"
        if 'kraj_nuts_kod' in document:
            # add decoded region name
            if decode_regions:
                if document['kraj_nuts_kod'] in regions_mapping:
                    document['kraj'] = regions_mapping[document["kraj_nuts_kod"]]
                else:
                    document['kraj'] = ""
            # reformat region code
            code = document['kraj_nuts_kod']
            document['kraj_nuts_kod'] = code[:2] + '-' + code[3:] # e.g. "CZ080" -> "CZ-080"
        json.dump(document, file)
        file.write('\n')

        docs += 1

    file.close()

url = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/zakladni-prehled.json'
filename = 'datasets/zakladni-prehled.json'
index = 'zakladni-prehled'
type = 'zakladni-prehled'
url_to_bulk_file(url, filename, index, type)

url = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/pomucky.json'
filename = 'datasets/pomucky.json'
index = 'pomucky'
type = 'pomucky'
url_to_bulk_file(url, filename, index, type)

url = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/osoby.min.json'
filename = 'datasets/osoby-s-prokazanou-nakazou.json'
index = 'osoby-s-prokazanou-nakazou'
type = 'osoby-s-prokazanou-nakazou'
url_to_bulk_file(url, filename, index, type, decode_regions=True)

url = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/kraj-okres-nakazeni-vyleceni-umrti.json'
filename = 'datasets/kraj-okres-nakazeni-vyleceni-umrti.json'
index = 'kraj-okres-nakazeni-vyleceni-umrti'
type = 'kraj-okres-nakazeni-vyleceni-umrti'
url_to_bulk_file(url, filename, index, type)
