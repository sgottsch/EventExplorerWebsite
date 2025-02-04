import datetime
import json
import math
import os
import re
from json import JSONDecodeError

from model.aspect import Aspect
from model.document import Document
from model.event import Event
from model.event_collections_data import EventCollectionsData
from model.ranking import Ranking
from model.summary import Summary, SummaryEntry
from model.timeline import Timeline, TimelineEntry
from event_explorer.countries import all_countries

K_all = 20
K_aspect = 10

JSON_ASPECTS = "Aspects"
JSON_EVENT_NAMES = "Event_Names"
JSON_GLOBAL_ASPECT = "Global_Ranking"
JSON_RANKING = "Document_Ranking"
JSON_RANKING_LIST = "Documents_List"

JSON_RANKING_OVERVIEW = "Overview"
JSON_RANKING_SUMMARY = "Summary"
JSON_RANKING_METADATA = "Metadata"
JSON_RANKING_TIMELINE = "Timeline"

JSON_DOCUMENT_TITLE = "Title"
JSON_DOCUMENT_SNIPPET = "Snippet"
JSON_DOCUMENT_ARCHIVE_URL = "Web Archive URL"
JSON_DOCUMENT_LIVE_URL = "Live Web URL"
JSON_DOCUMENT_URL = "URL"
JSON_DOCUMENT_DATE = "Date"

JSON_UPPER_ASPECT = "upper_aspect"

JSON_METADATA_DATE_START = "date range start"
JSON_METADATA_DATE_END = "date range end"
JSON_METADATA_LOCATIONS = "locations"
JSON_METADATA_SUBJECTS = "subjects"

JSON_TIMELINE_DATE = "Date"
JSON_TIMELINE_TEXT = "Text"
JSON_TIMELINE_DOCUMENT_IDS = "Articles"

# DATE_FORMAT = # TODO

ASPECTS_CAUSE = "Cause"
ASPECTS_RESULT = "Result"
ASPECTS_WHEN = "When"
ASPECTS_PARTICIPANTS = "who"
ASPECTS_LOCATIONS = "where"
ASPECTS_OTHER = "other"

input_date_formats = ["%d/%B/%Y", "%Y/%B/%d", "%Y/%m/%d", "%d %B %Y", "%b %#d, %Y", "%Y-%m-%d", "%d/%B/%Y","%Y/%B/%d", "%m/%d/%Y", "%d/%b/%Y", "%Y/%b/%d"]

output_date_format = "%b %#d, %Y"

ASPECT_DESCRIPTIONS = {ASPECTS_CAUSE: "Documents about the cause of the event.",
                       ASPECTS_RESULT: "Documents about the results/outcomes of the event.",
                       ASPECTS_WHEN: "Documents about important dates during the event.",
                       ASPECTS_PARTICIPANTS: "Documents about the humans involved in the event.",
                       ASPECTS_LOCATIONS: "Documents about the locations of the event.",
                       ASPECTS_OTHER: "Documents about other important entities involved in the event."}

ASPECTS_ORDER = [ASPECTS_CAUSE, ASPECTS_RESULT, ASPECTS_WHEN, ASPECTS_PARTICIPANTS, ASPECTS_LOCATIONS, ASPECTS_OTHER]


def format_date(date_str):
    date_str_cleaned = date_str.replace("th", "").strip()
    for date_format in input_date_formats:
        try:
            return datetime.datetime.strptime(date_str_cleaned, date_format).strftime(output_date_format)
        except ValueError as e:
            pass
    print("Wrong date format:", date_str)
    return date_str.strip()


def format_date_2(date_str):
    date_str_cleaned = date_str.replace("th", "").strip()
    for date_format in input_date_formats:
        try:
            return datetime.datetime.strptime(date_str_cleaned, date_format).strftime("%Y%m%d")
        except ValueError as e:
            pass
    print("Wrong date format:", date_str)
    return date_str.strip()


def create_timeline(timeline_json, documents_dict, top_k):
    date_dict = {}
    timeline_entry_id = 0
    for timeline_entry_json in timeline_json:
        text = timeline_entry_json[JSON_TIMELINE_TEXT]
        date = format_date(timeline_entry_json[JSON_TIMELINE_DATE])
        timeline_entry = TimelineEntry(id=timeline_entry_id, text=text, date=date)
        timeline_entry_id += 1
        # timeline.entries.append(timeline_entry)
        date_dict[format_date_2(timeline_entry_json[JSON_TIMELINE_DATE])] = timeline_entry
        document_ids = timeline_entry_json[JSON_TIMELINE_DOCUMENT_IDS]
        if len(document_ids) < top_k:  # never show ALL documents as references at once
            for document_id_str in document_ids:
                try:
                    timeline_entry.documents.append(
                        documents_dict[int(document_id_str.strip())])
                except KeyError:
                    print("Wrong reference in timeline:", document_id_str)

    # sort timeline entries chronologically
    timeline = Timeline()

    x = list(date_dict.keys())
    x.sort()
    for k in x:
        timeline.entries.append(date_dict[k])

    return timeline


def create_metadata(metadata_json):
    lines = ["Time range: " + format_date(metadata_json[JSON_METADATA_DATE_START]) + " – " + format_date(
        metadata_json[JSON_METADATA_DATE_END]),
             "Subjects: " + ", ".join(metadata_json[JSON_METADATA_SUBJECTS]),
             "Locations: " + ", ".join(metadata_json[JSON_METADATA_LOCATIONS])]

    return lines


def create_summary(summary_str, documents_dict, top_k):
    summary_str = summary_str.replace("=== End of Summary ===", "").replace("=== Summary ===", "").strip()

    if "\nReferences:\n" in summary_str:
        # In one case, the LLM added another "References:" list at the end
        summary_str = summary_str.split("\nReferences:\n")[0]

    parts = re.split('(\((?:[0-9],? ?)+\))', summary_str)

    summary = Summary()

    for part_no in range(0, len(parts), 2):
        entry = SummaryEntry(parts[part_no])
        summary.entries.append(entry)

        if part_no + 1 < len(parts):
            document_ids = re.findall(r'\d+', parts[part_no + 1])
            if len(document_ids) < top_k:  # never show ALL documents as references at once
                for document_id_str in document_ids:
                    try:
                        entry.documents.append(
                            documents_dict[int(document_id_str.strip())])
                    except KeyError:
                        print("Wrong reference in timeline:", document_id_str)

    return summary


def create_document_ranking(ranking_json, ranking, top_k=None):
    documents_dict = {}
    for document_id in ranking_json:
        if document_id == JSON_RANKING_LIST or document_id == JSON_RANKING_OVERVIEW or document_id == JSON_RANKING_TIMELINE:
            continue
        document_json = ranking_json[document_id]
        document = Document(document_id=int(document_id), title=document_json[JSON_DOCUMENT_TITLE],
                            snippet=document_json[JSON_DOCUMENT_SNIPPET],
                            date=document_json[JSON_DOCUMENT_DATE])
        if JSON_DOCUMENT_ARCHIVE_URL in document_json:
            document.archive_url = document_json[JSON_DOCUMENT_ARCHIVE_URL]
        if JSON_DOCUMENT_LIVE_URL in document_json:
            document.set_live_url(document_json[JSON_DOCUMENT_LIVE_URL])

        elif JSON_DOCUMENT_URL in document_json:
            document.set_live_url(document_json[JSON_DOCUMENT_URL])

        if top_k:
            if len(ranking.top_ranked_documents) < top_k:
                ranking.top_ranked_documents.append(document)
            else:
                ranking.all_ranked_documents.append(document)
        else:
            ranking.top_ranked_documents.append(document)
        documents_dict[document.id] = document
    return documents_dict


def load_data(folder_path, event_names_field=False):
    data = EventCollectionsData()

    for filename in os.listdir(folder_path):
        f = os.path.join(folder_path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            load_data_of_file(f, data)

    return data


def load_elections_overview(file_path, data):
    # the small countries (Andorra, San Marino, ...) must be added to the list last. Otherwise, they are not clickable on the map.
    small_countries = ["AND", "PMR", "SMR", "ABK", "MCO", "LIE"]
    small_countries_used = []

    with open(file_path) as f:
        countries = []
        done_country_ids = set()
        data_json = json.load(f)
        for country_id in data_json.keys():
            if country_id not in all_countries:
                print("Country ID missing:", country_id)
                continue
            if country_id in small_countries:
                small_countries_used.append(country_id)
            else:
                countries.append(all_countries[country_id])
            done_country_ids.add(country_id)

        for country_id in small_countries_used:
            countries.append(all_countries[country_id])

        data.countries = countries
        data.elections_overview = data_json


def load_data_of_file(file_path, data):
    if file_path.endswith("elections.json"):
        load_elections_overview(file_path, data)
    else:
        with open(file_path) as f:

            print("File", file_path)

            event_id = len(data.events)

            data_json = json.load(f)

            if JSON_EVENT_NAMES in data_json.keys():
                event_name = data_json[JSON_EVENT_NAMES]
            else:
                event_name = list(data_json.keys())[0]

            event = Event(event_id, event_name)

            data.event_name_to_id[event_name] = event_id

            data.events.append(event)
            data.events_dict[event_id] = event

            print("Load event", event.name)
            event_json = data_json[event.name]
            # event_json.aspects = event_json[JSON_ASPECTS]
            # data.aspects.append(JSON_GLOBAL_ASPECTS)

            if JSON_ASPECTS in event_json:
                aspects_json = event_json[JSON_ASPECTS]
            else:
                aspects_json = event_json

            event_aspects = {}

            for aspect_name in aspects_json:

                # ignore empty aspects
                if not event_json[aspect_name]:
                    continue  # TODO: This should never happen

                if aspect_name in event_aspects:
                    aspect = event_aspects[aspect_name]
                else:
                    aspect = Aspect(len(event_aspects), aspect_name)
                event_aspects[aspect_name] = aspect

                if JSON_UPPER_ASPECT in event_json[aspect_name] and event_json[aspect_name][JSON_UPPER_ASPECT] != "" and \
                        event_json[aspect_name][JSON_UPPER_ASPECT] != "no upper aspect":
                    upper_aspect_name = event_json[aspect_name][JSON_UPPER_ASPECT]

                    if upper_aspect_name in event_aspects:
                        upper_aspect = event_aspects[upper_aspect_name]
                    else:
                        upper_aspect = Aspect(len(event_aspects), upper_aspect_name)
                        if upper_aspect_name in ASPECT_DESCRIPTIONS:
                            upper_aspect.description = ASPECT_DESCRIPTIONS[upper_aspect_name]

                        event.aspects_dict[upper_aspect.id] = aspect
                        event_aspects[upper_aspect_name] = upper_aspect

                    upper_aspect.sub_aspects.append(aspect)

                # event.aspects.append(aspect)
                event.aspects_dict[aspect.id] = aspect
                if aspect_name in ASPECT_DESCRIPTIONS:
                    aspect.description = ASPECT_DESCRIPTIONS[aspect_name]
                ranking = Ranking(aspect=aspect)
                if JSON_RANKING_METADATA in event_json[aspect_name][JSON_RANKING_OVERVIEW]:
                    ranking.metadata = create_metadata(
                        event_json[aspect_name][JSON_RANKING_OVERVIEW][JSON_RANKING_METADATA])
                event.rankings[aspect] = ranking
                data.rankings[aspect] = ranking
                ranking_json = event_json[aspect_name][JSON_RANKING]
                documents_dict = create_document_ranking(ranking_json, ranking,
                                                         K_aspect)
                ranking.summary = create_summary(event_json[aspect_name][JSON_RANKING_OVERVIEW][JSON_RANKING_SUMMARY],
                                                 documents_dict, K_aspect)
                if JSON_RANKING_TIMELINE in event_json[aspect_name]:
                    ranking.timeline = create_timeline(event_json[aspect_name][JSON_RANKING_TIMELINE], documents_dict,
                                                       K_aspect)

            # order event aspects
            # first: preferred aspect order
            # second (order of entities): alphabetically
            # event_aspects_in_order = []
            event_aspects_others_alphabetically = []

            for aspect in event_aspects.values():
                if aspect not in event.rankings:
                    del event.aspects_dict[aspect.id]

            for aspect_name in ASPECTS_ORDER:
                if aspect_name in event_aspects:
                    aspect = event_aspects[aspect_name]
                    event.aspects.append(aspect)

            for aspect in event_aspects.values():
                aspect.sort_sub_aspects()

            event.aspects[len(event.aspects) - 1].is_last = True

            event.global_ranking = Ranking(JSON_GLOBAL_ASPECT)
            global_documents_dict = create_document_ranking(event_json[JSON_GLOBAL_ASPECT], event.global_ranking,
                                                            K_all)
            event.global_ranking.summary = create_summary(
                event_json[JSON_GLOBAL_ASPECT][JSON_RANKING_OVERVIEW][JSON_RANKING_SUMMARY], global_documents_dict,
                K_all)
            if JSON_RANKING_METADATA in event_json[JSON_GLOBAL_ASPECT][JSON_RANKING_OVERVIEW]:
                event.global_ranking.metadata = create_metadata(
                    event_json[JSON_GLOBAL_ASPECT][JSON_RANKING_OVERVIEW][JSON_RANKING_METADATA])
            if JSON_RANKING_TIMELINE in event_json[JSON_GLOBAL_ASPECT]:
                event.global_ranking.timeline = create_timeline(event_json[JSON_GLOBAL_ASPECT][JSON_RANKING_TIMELINE],
                                                                global_documents_dict, K_all)


if __name__ == '__main__':
    '''
    #str = '[ { "Date": "2017/June/14", "Text": "A massive fire engulfs Grenfell Tower in west London, leading to at least six casualties and residents being evacuated.", "Articles": ["7", "8", "15"] }, { "Date": "2017/June/16", "Text": "The death toll rises to 17, and it is suggested that some victims of the Grenfell Tower fire may never be identified.", "Articles": ["2", "5"] }, { "Date": "2017/June/18", "Text": "Concerns are raised about the preventability of the Grenfell Tower fire, and more actions are deemed necessary.", "Articles": ["15"] }, { "Date": "2017/August/5", "Text": "Regulation issues are discussed in the context of the Grenfell Tower fire, highlighting a decrease in regulations over two decades.", "Articles": ["1"] }, { "Date": "2017/August/15", "Text": "Witnesses report seeing a UFO in the sky above Grenfell Tower during the fire, adding a unique perspective to the tragic event.", "Articles": ["6"] } ]'

    documents_dict = {1: Document(1, "Test1", "", "", "Snippet1", "date1")}

    #for entry in create_timeline(str, documents_dict).entries:
    #    print(entry.text)

    summary_str = 'The Grenfell Tower fire in the United Kingdom occurred on June 14, 2017, leading to a death toll that may never be fully identified (2). The fire engulfed the tower in North Kensington, London, with at least six casualties reported (7). The incident prompted discussions on regulations and business practices related to the fire (1,4). Additionally, concerns were raised about the identification of victims and the use of banned cladding in Grenfell Tower (2,4). The tragedy sparked international responses, with leaders like Prime Minister Theresa May and Northern Ireland Prime Minister Justin Trudeau discussing regional issues (10).\n\n=== End of Summary ==='
    for entry in create_summary(summary_str, documents_dict).entries:
        print(entry.text)
    '''

    # data = {"user_study_pwa_en": load_data("../data/user_study_pwa_en/v4", event_names_field = True),
    #        "user_study_bing_en": load_data("../data/user_study_bing_en/v1")}

    data = {
        # "user_study_bing_en": load_data("../data/user_study_bing_en/v1"),
        "user_study_bing_en": load_data("../data/user_study_bing_en/v3"),
        "user_study_pwa_en": load_data("../data/user_study_pwa_en/v4"),
        "elections_bing_en": load_data("../data/elections_bing_en/v2")
    }

    # print(data["user_study_bing_en"].events_dict)
