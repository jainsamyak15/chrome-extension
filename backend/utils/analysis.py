from textblob import TextBlob
from keybert import KeyBERT
from googletrans import Translator
import nltk
import logging

logger = logging.getLogger(__name__)


class ContentAnalyzer:
    def __init__(self):
        try:
            # Import required NLTK data
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('brown', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('stopwords', quiet=True)

            self.key_model = KeyBERT()
            self.translator = Translator()
        except Exception as e:
            logger.error(f"Error initializing ContentAnalyzer: {str(e)}")
            raise

    def summarize(self, text, num_sentences=3):
        """Generate a summary of the text"""
        try:
            if not text:
                return ""

            blob = TextBlob(text)
            sentences = blob.sentences

            if len(sentences) <= num_sentences:
                return text

            # Score sentences based on word importance
            word_freq = {}
            for sentence in sentences:
                for word in sentence.words:
                    word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1

            sentence_scores = []
            for sentence in sentences:
                score = sum(word_freq.get(word.lower(), 0) for word in sentence.words)
                sentence_scores.append((score, sentence))

            # Get top sentences
            summary_sentences = sorted(sentence_scores, reverse=True)[:num_sentences]
            summary = ' '.join(str(sentence[1]) for sentence in sorted(summary_sentences, key=lambda x: str(x[1])))

            return summary

        except Exception as e:
            logger.error(f"Error in summarize: {str(e)}")
            return text

    def analyze_sentiment(self, text):
        """Analyze the sentiment of the text"""
        try:
            if not text:
                return {"sentiment": "neutral", "polarity": 0, "subjectivity": 0}

            blob = TextBlob(text)
            sentiment = blob.sentiment

            if sentiment.polarity > 0:
                sentiment_label = "positive"
            elif sentiment.polarity < 0:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"

            return {
                "sentiment": sentiment_label,
                "polarity": round(sentiment.polarity, 2),
                "subjectivity": round(sentiment.subjectivity, 2)
            }

        except Exception as e:
            logger.error(f"Error in analyze_sentiment: {str(e)}")
            return {"sentiment": "neutral", "polarity": 0, "subjectivity": 0}

    def extract_keywords(self, text, top_n=5):
        """Extract key phrases from the text"""
        try:
            if not text:
                return []

            keywords = self.key_model.extract_keywords(text,
                                                       top_n=top_n,
                                                       stop_words='english')
            return [keyword[0] for keyword in keywords]
        except Exception as e:
            logger.error(f"Error in extract_keywords: {str(e)}")
            return []

    def translate_text(self, text, target_lang='en'):
        """Translate text to target language"""
        try:
            if not text or target_lang == 'en':
                return text

            translation = self.translator.translate(text, dest=target_lang)
            return translation.text

        except Exception as e:
            logger.error(f"Error in translate_text: {str(e)}")
            return text