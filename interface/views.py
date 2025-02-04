from django.shortcuts import render

from event_explorer import urls
import datetime

allowed_modes = {"elections_bing_en": "Elections in Europe (Bing)",
                 "user_study_bing_en": "10 Example Events (Bing)",
                 "user_study_pwa_en": "10 Example Events (Arquivo.pt)",
                }

used_modes = allowed_modes.copy()
#for mode in urls.data:
#    used_modes[mode] = allowed_modes[mode]

# Create your views here.

def get_mode(mode:str = None):
    if mode is None or mode == "premio_arquivo_pt" or mode not in allowed_modes.keys():
        mode = "user_study_pwa_en"
    return mode



def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except Exception as e:
        return "-"

def index(request):
    context = {"title": "Start", "modes": used_modes, "showEventsList": False, "showEventCollections":  True}
    return render(request, "interface/index.html", context)

def contact(request):
    context = {"title": "Contact", "modes": used_modes, "showEventsList": False, "showEventCollections":  True}
    return render(request, "interface/contact.html", context)

def details(request):
    context = {"title": "About EventExplorer", "modes": used_modes, "showEventsList": False, "showEventCollections":  True}
    return render(request, "interface/details.html", context)

def index_mode(request, mode: str = None):

    print("LOG | index_mode | ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", get_client_ip(request), "|", mode)

    mode_fixed = get_mode(mode)
    if mode_fixed == "elections_bing_en":
        return elections(request)
    mode_name = None
    if mode != "premio_arquivo_pt":
        mode_name = allowed_modes[mode_fixed]
    context = {"title": "Start", "events": urls.data[mode_fixed].events, "mode": mode,
               "showEventsList": True, "showEventCollections":  mode != "premio_arquivo_pt", "modes": used_modes,
               "mode_name": mode_name}
    return render(request, "interface/index_mode.html", context)

def resources(request):
    context = {"title": "Resources", "showEventsList": True }
    return render(request, "interface/resources.html", context)

def event(request, event_id, mode:str = None):
    mode_fixed = get_mode(mode)

    event = urls.data[mode_fixed].events_dict[event_id]
    timeline = event.global_ranking.timeline

    print("LOG | event | ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|", event.name_nice, "|", get_client_ip(request), "|", mode)

    context = {"title": event.name_nice, "event": event, "aspects": event.aspects, "events": urls.data[mode_fixed].events,
               "ranking": event.global_ranking, "timeline": timeline, "mode": mode, "showEventsList": mode_fixed != "elections_bing_en",
               "showEventCollections":  mode != "premio_arquivo_pt", "modes": used_modes}
    return render(request, "interface/event.html", context)

def event_aspect(request, event_id, aspect_id, mode:str = None):

    mode_fixed = get_mode(mode)

    event = urls.data[mode_fixed].events_dict[event_id]
    aspect = event.aspects_dict[aspect_id]

    print("LOG | event_aspect | ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "|",event.name_nice, "|", aspect.name, "|", get_client_ip(request), "|", mode)

    ranking = event.rankings[aspect]
    timeline = ranking.timeline

    context = {"title": event.name_nice + " - " + aspect.name, "aspects": event.aspects, "event": event, "aspect": aspect, "ranking": ranking,
               "timeline": timeline, "events": urls.data[mode_fixed].events, "mode": mode, "showEventsList": mode_fixed != "elections_bing_en",
               "showEventCollections":  mode != "premio_arquivo_pt", "modes": used_modes}
    return render(request, "interface/event_aspect.html", context)


def elections(request):
    mode = "elections_bing_en"
    context = {"title": "Start", "events": urls.data[mode].events, "mode": mode, "elections": urls.data[mode].elections_overview,
               "countries": urls.data[mode].countries, "event_names_to_id":  urls.data[mode].event_name_to_id, "showEventsList": False,
               "showEventCollections": True, "modes": used_modes}
    number_of_elections = 0
    for country in urls.data[mode].countries:
        number_of_elections += len(urls.data[mode].elections_overview[country["id"]])
    print("number_of_elections:", number_of_elections)
    return render(request, "interface/index_elections.html", context)
