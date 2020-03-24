from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


def plot_word_cloud(df, text_col, max_words=500):
    text_data = df[text_col]
    plt.figure(figsize=(16, 13))

    wc = WordCloud(background_color="black",
                   max_words=500,
                   stopwords=STOPWORDS,
                   max_font_size=40)

    wc.generate(" ".join(text_data))
    plt.title("Twitter Raw Dataset", fontsize=20)
    plt.imshow(wc.recolor(colormap='Pastel2', random_state=17), alpha=0.98)
    plt.axis('off')