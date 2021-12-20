from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class Vectorizer:
    """Vectorizer class to calculate similarity between source documents and a target

    example usage:
        vectorizer = Vectorizer()

        similarity_score,_ = vectorizer.get_similarity_score(
            list_source_texts = [
                text_kvk_uittreksel1,
                text_kvk_uittreksel2,
                text_kvk_uittreksel3
            ],
            target_text = text
        )
    """

    def __init__(self, *args, **kwargs):
        self.vectorizer = TfidfVectorizer(*args, **kwargs)

    def vectorize(self, list_source_texts, target_text):
        return self.vectorizer.fit_transform(list_source_texts + [target_text])

    @staticmethod
    def convert_sparse_matrix_to_result(sparse_matrix):
        """function to convert the Sparse matrix to something human readable

        Parameters
        ----------
        sparse_matrix

        Returns
        -------
        np.array
        """
        arr_result = (sparse_matrix * sparse_matrix.T).toarray()
        np.fill_diagonal(arr_result, np.nan)
        return arr_result

    def get_similarity_score(self, list_source_texts: list, target_text: str):
        """Function that takes source documents and a single target and returns the similarity score and best match.

        Parameters
        ----------
        list_source_texts : list
            source texts
        target_text: str
            target document of interest

        Returns : tuple
            the best match score and the actual best matched textx
        -------
        """
        arr_result = Vectorizer.convert_sparse_matrix_to_result(
            self.vectorize(list_source_texts, target_text)
        )

        # we are only really interested in the source with target hence take last row of arr
        results = arr_result[-1]

        text_best_match = list_source_texts[
            np.nanargmax(results)
        ]  # this would give the best match

        return np.nanmax(results), text_best_match
