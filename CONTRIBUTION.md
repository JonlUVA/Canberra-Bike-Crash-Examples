COMP7230 Group Project
Winter Semester, 2021

# _Canberra: Changing Gears on Bike Safety_
_An investigation on the uphill battle facing cyclists_

## Statement of Contributions

We declare that work for our project was distributed among the group members,
and the main contributions were as follows:

* Jonathon Longden (u7333077) --- 33%
  - [cycling_data_integration](cycling_data_integration.py)
    - This program reads the processed data and produces a dictionary which contains dataframes, the first which contains the estimated number of cyclists in Canberra on any given day, as recorded by the ACT bike-barometer, and the daily estimated rainfall as measured by the  Canberra airport weather station.
    - The second containing the bike-crash information as recorded by the AFP and the reported rainfall of the day from the closest weather station in the region to this particular crash, and if the crash happened after sunset or before sunrise the number of streetlights within a 30m proximity.
  - Wrote report
  - Wrote unit tests

* Tim Arney (u7378856) --- 33%
  - [cycling_check_dependencies](cycling_check_dependencies.py): To programmatically scan all source code for module dependencies and check host system against required modules
  - [cycling_update_compatible_systems](cycling_update_compatible_systems.py): To automatically update [REQUIREMENTS.md](REQUIREMENTS.md) with module versioning information if host system passes dependency check
  - [cycling_download_data](cycling_download_data.py): To read CSV file of data source information, download each dataset, and create/amend a [.gitignore](.gitignore) file to keep datasets from syncing to git repository
  - [cycling_load_data](cycling_load_data.py): To read CSV file of data source information, look for locally stored copies of each dataset, download if unavailable, then load each dataset into the appropriate data structure.  Tabular data that includes date/time and/or lat/long fields are additionally preprocessed based on field information provided in the data source CSV to normalise fields in preparation for data matching.  More complex data such as Rainfall data and Suburb GIS data are loaded into custom classes to provide additional functionality.  In the case of Rainfall data, in addition to the tabular data, weather station information is extracted from an associated text file such as each station's latitude and longitude and a class method is provided to calculate the haversine distance from any point to the station.  In the case of Suburb GIS data, class methods are provided to translate any latitude and longitude to its containing suburb and district.
  - [cycling_helper_functions](cycling_helper_functions.py): To provide some additional generic functions such as reading and writing DataFrames to Excel and CSV to facilitate not having to repeat computationally expensive analysis write such data to disk on first execution and read it from disk on subsequent executions.
  - [cycling_main](cycling_main.py): A central module to integrate and execute all aspects of the project.
  - Maintained [MEETINGS.md](MEETINGS.md) until it was deprecated in favour of a group Discord channel.
  - Maintained gitlab repository.
  - Prepared [NOTES.md](NOTES.md).

* Hugh Porter (u7398670) --- 33%
  - Developed classes XYZ
  - Managed meetings, maintained gitlab
