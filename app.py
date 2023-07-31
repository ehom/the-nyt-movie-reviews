import streamlit as st
import time
from calendar import timegm
from datetime import datetime
import dateutil.parser as dp
import dataset.movie_reviews


def iso_to_epoch_time(iso_date_str):
    # Parse the ISO date string and convert it to a datetime object
    parsed_datetime = datetime.fromisoformat(iso_date_str)

    # Get the UTC timestamp from the datetime object
    timestamp = timegm(parsed_datetime.utctimetuple())

    return timestamp


def iso_to_how_long_ago(iso_date_str):
    t0_past = iso_to_epoch_time(iso_date_str)
    t1_now = int(time.time())

    time_difference = t1_now - t0_past

    # Get the time components (days, seconds, etc.) from the time difference
    days = round(time_difference / (60 * 60 * 24))
    seconds = round(time_difference)

    if days > 7:
        weeks = days // 7
        return f"{weeks} {'week' if weeks == 1 else 'weeks'} ago"
    elif days > 0:
        return f"{days} {'day' if days == 1 else 'days'} ago"
    elif seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    else:
        return "Just now"


ATTRIBUTION = "[Data provided by The New York Times](https://developer.nytimes.com)"
CLAPPING = "\U0001F44F"

menu_items = {
  "About": "Data provided by The New York Times"
}


def view(articles):
    st.set_page_config(page_title="The NYT Movie Reviews",
                       page_icon="\U0001F3A5",
                       layout="wide",
                       menu_items=menu_items)

    st.title("Movie Reviews")
    st.markdown(ATTRIBUTION)
    st.divider()

    for article in articles:
        if article['section'] != "movies":
            continue

        column1, column2 = st.columns([4, 1])

        with column1:
            st.write(iso_to_how_long_ago(article['published_date']))
            title = article['title']
            url = article['url']

            text = f"[{title}]({url})"
            st.subheader(text)
            st.write(article['abstract'])
            if len(article['kicker']) > 0:
                kicker = "{} {}".format(article['kicker'], CLAPPING * 3)
                st.write(kicker)
            if len(article['per_facet']):
                iterator = map(lambda item: f"[{item}]", article['per_facet'])
                st.write(' '.join(list(iterator)))

        with column2:
            st.image(article['multimedia'][-1]['url'])

        st.divider()

    st.markdown(ATTRIBUTION)


if 'articles' not in st.session_state:
    st.session_state['articles'] = []
    object = dataset.movie_reviews.load()

    st.session_state['articles'] = object['results']

view(st.session_state['articles'])
