import re
import time
from calendar import timegm
from datetime import datetime
import streamlit as st
from annotated_text import annotated_text
import dateutil.parser as dp
import dataset.movie_reviews

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4, width=40)


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


def find_movie_name(descriptions):
    movie_name = None
    for desc in descriptions:
        pattern = r'(.+) \(Movie\)'
        matches = re.search(pattern, desc)
        if matches:
            print("movie name:", matches.groups())
            print("movie name:", matches.group(0))
            return matches.groups()[-1]
    return movie_name


def prepare_text_for_annotation(list_of_people):
    people = []

    if len(list_of_people):
        for person in list_of_people:
            pattern = r'(.+) \(([\w\s]+)\)'
            matches = re.search(pattern, person)
            if matches:
                print("matches:", matches.group(0))
                print("match:", matches.groups()[-1])
                name = matches.groups()[0]
                role = matches.groups()[-1]
                people.append((name, role))
            else:
                people.append((person, "Actor"))

            people.append(" ")

    print(people)

    return people


def display(article):
    # st.image(article['multimedia'][0]['url'])
    # st.image(article['multimedia'][1]['url'])
    st.write(iso_to_how_long_ago(article['published_date']))
    title = article['title']
    url = article['url']

    text = f"[{title}]({url})"
    st.subheader(text)
    st.write(article['abstract'])

    prepared_text = prepare_text_for_annotation(article['per_facet'])
    annotated_text(prepared_text)

    if article['kicker']:
        kicker = article['kicker']
        annotated_text((kicker, "", "#FFD700"))


def view(title, articles):
    count = len(articles)

    st.title(f"{title} ({count})")
    st.markdown(ATTRIBUTION)

    st.divider()

    print("# of movie reviews:", len(articles))

    for index in range(0, len(articles), 3):
        columns = st.columns(3)
        slices = articles[index: index + 3]

        for slice_index, slice in enumerate(slices):
            with columns[slice_index]:
                st.image(articles[index + slice_index]['multimedia'][-1]['url'])
                # TODO: Save actual movie name with the Movie Review
                movie_name = find_movie_name(articles[index + slice_index]['des_facet'])
                if movie_name:
                    st.button(movie_name)
                else:
                    st.button("?", key=articles[index+slice_index]['title'])
    st.divider()

    st.markdown(ATTRIBUTION)


def view_news(title, articles):
    count = len(articles)

    st.title(f"{title} ({count})")
    st.markdown(ATTRIBUTION)

    st.divider()

    print("# of movie reviews:", len(articles))

    for article in articles:
        columns = st.columns([4, 1])

        with columns[0]:
            display(article)

        with columns[1]:
            st.image(article['multimedia'][-1]['url'])

        st.divider()

    st.markdown(ATTRIBUTION)


def view_collage(title, articles):
    count = len(articles)

    st.title(f"{title} ({count})")
    st.markdown(ATTRIBUTION)

    st.divider()

    print("# of movie reviews:", len(articles))

    for index in range(0, len(articles), 5):
        columns = st.columns(5)
        slices = articles[index: index + 5]

        for slice_index, slice in enumerate(slices):
            with columns[slice_index]:
                st.image(articles[index + slice_index]['multimedia'][-1]['url'])
    st.divider()

    st.markdown(ATTRIBUTION)


def movie_review_filter(article):
    if article['section'] != "movies":
        return False 

    if "Review" not in article['title']:
        return False 
    return True


def critics_choice_filter(article):
    if article['section'] != "movies":
        return False 

    if "Review" not in article['title']:
        return False

    if "Critic" not in article['kicker']:
        return False
 
    return True


def related_news_filter(article):
    return not movie_review_filter(article)


def main():
    st.set_page_config(page_title="The NYT Movie Reviews",
                       page_icon="\U0001F3A5",
                       layout="wide",
                       menu_items=menu_items)

    if 'articles' not in st.session_state:
        object = dataset.movie_reviews.load()
        st.session_state['articles'] = object['results']
        # extract movie reviews from articles

        st.session_state['reviews'] = list(filter(movie_review_filter, st.session_state['articles']))

        # TODO: Maybe better to same the indices instead of copying the articles to 
        # each section of the session state

        st.session_state['news'] = list(filter(related_news_filter, st.session_state['articles']))
        st.session_state['critics'] = list(filter(critics_choice_filter, st.session_state['reviews']))

    # pp.pprint(st.session_state['reviews'])
   
    radio_selection = None
 
    with st.sidebar:
        st.header("The NYT Movie Reviews")

        radio_selection = st.radio("View", ["Movie Reviews", "Critic\u2019s Pick", "Related News", "Collage"])

    if radio_selection == "Related News": 
        view_news("Related News", st.session_state['news'])
    elif "Critic" in radio_selection:
        view_news("Critic\u2019s Pick", st.session_state['critics'])
    elif  "Collage" in radio_selection:
        view_collage("Collage", st.session_state["articles"])
    else:
        # view("Movie Reviews", st.session_state['reviews'])
        view_news("Movie Reviews", st.session_state['reviews'])


if __name__ == "__main__":
    main()

