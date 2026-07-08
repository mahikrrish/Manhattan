"""
Natural Language Processing module for the Manhattan project.

This module defines the NaturalLanguageProcessing class, which is responsible
for performing spaCy-based text preprocessing on speech-to-text output generated
by the Speech Recognition component.

Current responsibilities of this module:
- Convert raw transcription text into a spaCy Doc object.
- Extract sentence-level segmentation from the transcription.
- Perform Named Entity Recognition (NER).
- Build an entity summary grouped by entity labels.
- Perform token-level linguistic analysis such as token text, lemma, and
  part-of-speech (POS) tagging.
- Log component performance details such as start time, end time, duration,
  execution status, and error information into the performance monitoring table.

This module acts as an intermediate NLP processing layer in Manhattan's
pipeline, where transcribed text is enriched with structured linguistic
information before being passed to downstream components.

The class supports two execution patterns:
1. preprocessing():
   Used when the caller wants the direct NLP output only. If NLP processing
   fails, this method returns None after recording the failure in the
   performance monitoring table.

2. run():
   Used as the assistant-facing execution method. If NLP processing succeeds,
   it returns the complete structured NLP package. If NLP processing fails,
   it returns a fallback dictionary containing the original text and None for
   NLP-derived fields so that downstream components can still access the raw
   transcription.

Dependencies:
- spaCy
- en_core_web_sm model
- database module for performance logging
- threading, datetime, time, warnings
"""

import threading
from datetime import datetime
import time
import warnings
import database
import spacy
warnings.filterwarnings('ignore') #To suppress all warnings across the entire script


class NaturalLanguageProcessing(threading.Thread):
    """
    Reusable Natural Language Processing component for the Manhattan project.

    This class loads the spaCy English language pipeline once and reuses it to
    process multiple transcription texts. For each supplied text, it can build a
    structured NLP output package containing sentence detection, named entities,
    grouped entity summaries, and token-level linguistic analysis.

    The class also records execution timings and logs success or failure details
    into the performance monitoring system for each processed input text. Each
    performance log can optionally be linked to a specific conversation_history
    row through a conversation_id so that component-level monitoring records can
    be traced back to the corresponding end-to-end conversation run.

    Execution patterns:
        1. preprocessing(raw_text, conversation_id):
           Used when the caller wants the direct NLP output only. If NLP
           processing fails, this method returns None after recording the
           failure in the performance monitoring table.

        2. run(raw_text, conversation_id=None):
           Used as the assistant-facing execution method. If NLP processing
           succeeds, it returns the complete structured NLP package. If NLP
           processing fails, it returns a fallback dictionary containing the
           original text and None for NLP-derived fields so that downstream
           components can still access the raw transcription.

    Attributes:
        nlp (spacy.language.Language):
            Loaded spaCy English language pipeline used for text processing.

        performance_log (dict):
            Dictionary used to capture component-level execution metadata such as
            conversation_id, component name, start time, end time, duration,
            status, and error_message for database logging.
    """
    def __init__(self):
        """
        Initialize the NaturalLanguageProcessing component.

        This constructor loads the spaCy English language model once and initializes
        the performance logging dictionary for the NLP component. The resulting
        object can then be reused to process multiple transcription texts through
        the preprocessing(raw_text) or run(raw_text) methods.

        Raises:
            OSError:
                If the spaCy language model 'en_core_web_sm' is not installed or
                cannot be loaded.

            Exception:
                Propagates any unexpected initialization error encountered during
                spaCy model loading.
        """
        threading.Thread.__init__(self)
        self.nlp = spacy.load('en_core_web_sm')
        self.performance_log = {}
        self.performance_log['component'] = 'NaturalLanguageProcessing'

    def run(self, raw_text, conversation_id=None):
        """
        Execute the NLP pipeline for a single transcription text and return either
        structured NLP output or a fallback dictionary.

        This method acts as the assistant-facing execution entry point for the NLP
        component. It calls preprocessing(raw_text, conversation_id) to generate the
        structured NLP package for the supplied transcription text.

        Behavior:
            - If preprocessing succeeds, the structured NLP output dictionary is
            returned.
            - If preprocessing fails and returns None, this method returns a
            fallback dictionary containing the original transcription text and
            None for NLP-derived fields. This ensures that downstream components,
            such as the LLM layer, can still access the original text even when
            NLP preprocessing fails.

        Args:
            raw_text (str):
                Raw transcription text to be processed by the NLP pipeline.

            conversation_id (int | None, optional):
                Primary key of the corresponding conversation_history row for the
                current conversation run. When provided, the NLP component's
                performance monitoring record is linked to that conversation row.
                Defaults to None.

        Returns:
            dict:
                On successful NLP processing, returns a dictionary containing:
                - original_text
                - sentences
                - entities
                - entity_summary
                - token_analysis

                On NLP failure, returns a fallback dictionary of the form:
                {
                    "original_text": <raw transcription text>,
                    "sentences": None,
                    "entities": None,
                    "entity_summary": None,
                    "token_analysis": None
                }
        """
        processed_text = self.preprocessing(raw_text, conversation_id)
        if processed_text:
            return processed_text
        else:
            return {
                'original_text': raw_text,
                'sentences': None,
                'entities': None,
                'entity_summary': None,
                'token_analysis': None
            }

    def preprocessing(self, raw_text, conversation_id):
        """
        Build the complete NLP output package for a single transcription text.

        This method is the main orchestration layer of the NLP component. It first
        converts the supplied raw transcription text into a spaCy Doc object and
        then performs the following operations:

        1. Extract the original text from the Doc.
        2. Perform sentence detection.
        3. Perform Named Entity Recognition (NER).
        4. Generate an entity summary grouped by entity label.
        5. Perform token-level analysis, including token text, lemma, and
        part-of-speech (POS).

        The method also records execution timings and logs success or failure
        information into the performance monitoring system. If a conversation_id is
        supplied, the resulting performance-monitor entry is linked to the matching
        conversation_history row for the current end-to-end conversation run.

        Args:
            raw_text (str):
                Raw transcription text to be processed.

            conversation_id (int | None):
                Primary key of the conversation_history row representing the current
                conversation run. This value is stored in the NLP performance log so
                that the component-level performance record can be linked back to the
                main conversation entry. If no conversation row has been created yet,
                None may be passed.

        Returns:
            dict | None:
                On success, returns a dictionary containing the processed NLP output
                with the following keys:

                - original_text (str):
                    Original transcription text.

                - sentences (list[str]):
                    List of sentence strings extracted from the transcription.

                - entities (list[dict] | None):
                    List of detected named entities, where each entity is
                    represented as a dictionary containing:
                        - text: entity text
                        - label: spaCy entity label
                    Returns None if no entities are detected.

                - entity_summary (dict | None):
                    Dictionary grouping entity texts by their entity label.
                    Example:
                    {
                        "PERSON": ["Narendra Modi"],
                        "GPE": ["Japan"]
                    }
                    Returns None if no entities are detected.

                - token_analysis (list[dict] | None):
                    List of token-level linguistic details, where each token is
                    represented as a dictionary containing:
                        - text: original token text
                        - lemma: lemmatized/base form of the token
                        - pos: part-of-speech tag
                    Returns None if token analysis produces no tokens.

                On failure, returns None after recording the failure details in the
                performance monitoring table.

        Notes:
            This method is suitable for direct NLP evaluation and bulk testing
            scenarios where the caller wants to distinguish between successful NLP
            processing and NLP failure using a None return value.
        """
        self.performance_log['start_time'] = time.time()
        self.performance_log['conversation_id'] = conversation_id
        self.raw_text = self.nlp(raw_text)
        try:
            preprocessed_text = {
                'original_text': self.raw_text.text,
                'sentences': self.sentence_detection(self.raw_text),
                'entities': self.named_entity_recognition(self.raw_text),
                'entity_summary': self.entity_summary(self.raw_text),
                'token_analysis': self.token_analysis(self.raw_text)
            }
            self.performance_log['status'] = 'Success'
            self.performance_log['error_message'] = None
            return preprocessed_text
        except Exception as e:
            self.performance_log['error_message'] = str(e)
            self.performance_log['status'] = 'Error'
            return None
        finally:
            self.performance_log['end_time'] = time.time()
            self.performance_monitor()

    def sentence_detection(self, text):
        """
        Extract sentence strings from a spaCy Doc object.

        This method uses spaCy sentence segmentation to split the supplied Doc
        into individual sentences and returns them as a list of strings.

        Args:
            text (spacy.tokens.doc.Doc):
                spaCy Doc object containing the transcription text to be split
                into sentences.

        Returns:
            list[str]:
                List of sentence strings detected in the transcription.

        Raises:
            Exception:
                Raised if no sentences are detected in the supplied text, or if
                any unexpected error occurs during sentence extraction.
        """
        try:
            sentence = [str(sentence).strip() for sentence in text.sents if str(sentence).strip()]
            if sentence:
                return sentence
            else:
                raise Exception('No sentences detected')
        except Exception as e:
            raise

    def named_entity_recognition(self, preprocessed_text_sentence):
        """
        Perform Named Entity Recognition (NER) on a spaCy Doc object.

        This method extracts all named entities identified by spaCy in the
        supplied Doc and returns them as a list of dictionaries. Each dictionary
        contains the entity text and its corresponding entity label.

        Args:
            preprocessed_text_sentence (spacy.tokens.doc.Doc):
                spaCy Doc object on which named entity recognition is to be
                performed.

        Returns:
            list[dict] | None:
                A list of dictionaries representing detected named entities.
                Each dictionary contains:
                    - text (str): the entity text
                    - label (str): spaCy entity label for the entity

            Returns None if no named entities are detected.

        Raises:
            Exception:
                Propagates any unexpected error encountered during entity
                extraction.
        """
        try:
            ner = [
                {'text': token.text, 'label': token.label_}
                for token in preprocessed_text_sentence.ents
            ]
            if ner:
                return ner
            else:
                return None
        except Exception as e:
            raise
    def entity_summary(self, preprocessed_text_sentence):
        """
        Build a grouped summary of named entities by entity label.

        This method iterates through the named entities detected in the supplied
        spaCy Doc object and groups them into a dictionary keyed by entity
        labels such as PERSON, ORG, DATE, GPE, and others.

        Example output:
            {
            "PERSON": ["Narendra Modi", "Sanae Takaichi"],
            "GPE": ["India", "Japan"],
            "DATE": ["tomorrow"]
            }

        Args:
            preprocessed_text_sentence (spacy.tokens.doc.Doc):
                spaCy Doc object whose named entities are to be grouped.

        Returns:
            dict | None:
                Dictionary mapping each entity label to a list of entity texts.
                Returns None if no named entities are detected.

        Raises:
            Exception:
            Propagates any unexpected error encountered while building the
            grouped entity summary.
        """
        try:
            entity_summary = {}
            for token in preprocessed_text_sentence.ents:
                if entity_summary.get(token.label_):
                    entity_summary[token.label_].append(token.text)
                else:
                    entity_summary[token.label_] = [token.text]
            if entity_summary:
                return entity_summary
            else:
                return None
        except Exception as e:
            raise
    def token_analysis(self, preprocessed_text_sentence):
        """
        Perform token-level linguistic analysis on a spaCy Doc object.

        This method iterates through all tokens present in the supplied spaCy
        Doc and extracts token-level linguistic metadata such as:

        - text: original token text
        - lemma: lemmatized/base form of the token
        - pos: part-of-speech tag assigned by spaCy

        Args:
            preprocessed_text_sentence (spacy.tokens.doc.Doc):
                spaCy Doc object whose tokens are to be analyzed.

        Returns:
            list[dict] | None:
                List of dictionaries containing token-level linguistic
                information. Each dictionary contains:
                    - text (str): original token text
                    - lemma (str): lemmatized/base form of the token
                    - pos (str): part-of-speech tag

                Returns None if no tokens are available for analysis.

        Raises:
            Exception:
            Propagates any unexpected error encountered during token
            analysis.
        """
        try:
            analyzed_token = [
                {'text': token.text, 'lemma': token.lemma_, 'pos': token.pos_}
                for token in preprocessed_text_sentence
            ]
            if analyzed_token:
                return analyzed_token
            else:
                return None
        except Exception as e:
            raise
    def performance_monitor(self):
        """
        Log NLP component execution details to the performance monitoring table.

        This method finalizes the NLP component's performance log by adding:
            - created_at timestamp
            - execution duration

        It then forwards the performance metadata to the database logging layer for
        insertion into the performance_monitor table.

        The performance log is expected to contain:
            - conversation_id
            - component
            - start_time
            - end_time
            - status
            - error_message

        The conversation_id field links the component-level NLP performance record
        to the corresponding row in conversation_history so that the full
        conversation run and its internal component timings can be analyzed
        together.

        Side Effects:
            Inserts a performance monitoring record into the database via
            database.log().performance_monitor(data=self.performance_log).

        Returns:
            None
        """
        now = datetime.now()
        self.performance_log['created_at'] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.performance_log['duration'] = (self.performance_log['end_time'] -
                                            self.performance_log['start_time'])
        database.log().performance_monitor(data=self.performance_log)
