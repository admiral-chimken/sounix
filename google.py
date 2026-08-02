import webbrowser
import urllib.parse



def google_search(query):

    url = (


           "https://www.google.com/search?q="

           + urllib.parse.quote_plus(query)

     )



     webbrowser.open(url)

     return f"sounix: Opening google search for (query)'."
