from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)
app.config['DEBUG'] = True

def get_meme(attempts=5):
    try:
        inappropriate_subreddits = ["dankmemes", "ImGoingToHellForThis", "OffensiveMemes"]
        url = "https://meme-api.com/gimme"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        app.logger.info(f"API Response: {data}")

        subreddit = data["subreddit"]

        if subreddit in inappropriate_subreddits:
            if attempts > 0:
                app.logger.info(f"Inappropriate subreddit: {subreddit}, retrying...")
                return get_meme(attempts - 1)
            else:
                app.logger.warning("Reached maximum attempts for getting a meme")
                return None, None

        meme_large = data["preview"][-2]
        return meme_large, subreddit

    except requests.Timeout:
        app.logger.error("Request timed out")
        return None, None
    except requests.RequestException as e:
        app.logger.error(f"Request failed: {e}")
        return None, None
    except (KeyError, IndexError) as e:
        app.logger.error(f"Error processing response: {e}")
        return None, None

@app.route("/")
def index():
    return redirect(url_for('meme'))

@app.route("/meme")
def meme():
    meme_pic, subreddit = get_meme()
    if meme_pic and subreddit:
        return render_template("meme_index.html", meme_pic=meme_pic, subreddit=subreddit)
    else:
        return render_template("error.html"), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
