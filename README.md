# EventExplorer, an Interactive System for Exploring Event Collections (Website)

This is a Django Web app to run the EventExplorer website. With the Event-Explorer website, you can explore event collections created using the EventExplorer approach available in [a separate GitHub repository](https://github.com/saraabdollahi/EventExplorer).

The main repository containing more information about EventExplorer and its retrieval & ranking model are available in [the main EventExplorer GitHub repository](https://github.com/saraabdollahi/EventExplorer).

## Data

This repository comes with three example event collections:
- Elections in Europe (Bing)
   - With map visualisation
- 10 Example Events (Bing)
- 10 Example Events (Arquivo.pt)

For details about these collections, please refer to our paper (see bottom).

# Installation

1. Install the required libraries via `pip install -r requirements.txt`.
2. Run the Web app via `python manage.py runserver`.
3. Access the Web app in the browser on [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (or on another configured port).

# Adding New Event Collections

To add more event collections

1. Generate JSON files of your event collection using the [EventExplorer repository](https://github.com/saraabdollahi/EventExplorer).
2. Create a new folder call in `data`. Within that folder, create a folder `v1` and insert the generated .json files.
3. Add a new entry to the `data` dictionary in [event_explorer/urls.py](event_explorer/urls.py) to establish an identifier of your new event collection and the location of your new folder.
4. Add a new entry to the `allowed_modes` dictionary in [event_explorer/interface/views.py](event_explorer/interface/views.py) to establish the label of your new event collection.

# Further Individualisation

To configure your contact information and/or fix file path issues, check the following files:

- Update contact in [event_explorer/interface/templates/interface/contact.html](event_explorer/interface/templates/interface/contact.html)
- Change `base_folder` in [event_explorer/urls.py](event_explorer/urls.py)
- Set `sys.path.append()` in [event_explorer/wsgi.py](event_explorer/wsgi.py)
- Extend `ALLOWED_HOSTS` in [event_explorer/settings.py](event_explorer/settings.py)

# Contact

Simon Gottschalk ([gottschalk@L3S.de](mailto:gottschalk@L3S.de)). Please also refer to the [main EventExplorer GitHub repository](https://github.com/saraabdollahi/EventExplorer).

# Reference

See the [main EventExplorer GitHub repository](https://github.com/saraabdollahi/EventExplorer).