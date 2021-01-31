import nltk
import re

class LogicEngine:
    def __init__(self, table, grammar_file_path):
        (entities, events, beatat, tournament_matches_metadata) = self.__parse_table(table)

        self.tournament_matches_metadata = tournament_matches_metadata

        domain_string = self.__constructDomainString(entities, events, beatat)
        grammar_string = self.__constructGrammarString(grammar_file_path, entities, events)

        val = nltk.Valuation.fromstring(domain_string)

        self.assignment = nltk.Assignment(val.domain)
        self.model = nltk.Model(val.domain, val)

        self.grammar = nltk.grammar.FeatureGrammar.fromstring(grammar_string)

    def answer(self, sentence):
        words = sentence.split(" ")
        sanatized_sentence = " ".join(list(map(self.__sanatizeWord, words)))
        try:
            results = nltk.evaluate_sents([sanatized_sentence], self.grammar, self.model, self.assignment)
            (_, logical_expression, value) = results[0][0]
            (response, new_value) = self.__format_response(logical_expression)
            return (logical_expression, new_value, response)
        except:
            return ("", None, "")

    def __format_response(self, expression):
        (value, entity1_name, entity2_name, event_name, entity_a_score, entity_b_score, tournament_round_name) = self.tournament_matches_metadata[str(expression)]
        answer = "{0}, {1} beat {2} in a {3}-{4} match. From what I can see, they played in {5} at {6}".format(value, entity1_name, entity2_name, entity_a_score, entity_b_score, tournament_round_name, event_name)
        return (answer, value)

    def __parse_table(self, table):
        entities = set()
        events = set()
        beatat = set()
        tournament_matches_metadata = dict()

        for (entity_a_score, entity_b_score, tournament_round_name, winner_name, entity1_name, entity2_name, event_name) in table:
            # Sanatize the words
            entity1_name_sanatized = self.__sanatizeWord(entity1_name)
            entity2_name_sanatized = self.__sanatizeWord(entity2_name)
            event_name_sanatized = self.__sanatizeWord(event_name)

            # Track entities and event
            entities.add(entity1_name_sanatized)
            entities.add(entity2_name_sanatized)
            events.add(event_name_sanatized)

            # Modify sanitized words to match natural language toolkit's assertion response
            entity1_name_sanatized_modified = entity1_name_sanatized.replace(" ", "_")
            entity2_name_sanatized_modified = entity2_name_sanatized.replace(" ", "_")
            event_name_sanatized_modified = event_name_sanatized.replace(" ", "_")

            # Track the tournament match for answers later
            tournament_matches_metadata["beatat({0},{1},{2})".format(entity1_name_sanatized_modified, entity2_name_sanatized_modified, event_name_sanatized_modified)] = (True, entity1_name, entity2_name, event_name, entity_a_score, entity_b_score, tournament_round_name)
            tournament_matches_metadata["beatat({0},{1},{2})".format(entity2_name_sanatized_modified, entity1_name_sanatized_modified, event_name_sanatized_modified)] = (False, entity1_name, entity2_name, event_name, entity_a_score, entity_b_score, tournament_round_name)


            # Construct beatat relation
            if winner_name == entity1_name:
                beatat.add((entity1_name_sanatized, entity2_name_sanatized, event_name_sanatized))
            else:
                beatat.add((entity2_name_sanatized, entity1_name_sanatized, event_name_sanatized))
        
        return (entities, events, beatat, tournament_matches_metadata)
    
    def __sanatizeWord(self, word):
        word = re.sub("[^0-9A-Za-z ]", "" , word)
        word = re.sub("\s+"," ", word)
        word = word.lower()
        return word

    def __constructGrammarString(self, grammar_file_path, entities, events):
        grammar_string_partial = open(grammar_file_path, 'r').read()

        entities_string = self.__addGrammarStringEntity(
            self.__addGrammarStringEntity(
                "", entities, "PLAYER"), 
            events, "EVENT")

        grammar_string = grammar_string_partial.replace("{entities}", entities_string)
        return grammar_string

    def __addGrammarStringEntity(self, inputString, entities, nt_name):
        for entity in entities:
            split_entity = entity.split(' ')
            current_entity_string = ""
            for word in split_entity:
                current_entity_string = current_entity_string + "'{0}' ".format(word)
            inputString = inputString + "{0}[SEM=<\P.P({1})>] -> {2}\n".format(nt_name, "_".join(split_entity), current_entity_string)
            
        return inputString


    def __constructDomainString(self, entities, events, beatat):
        # Construct domain string
        domainString = self._addDomainStringTreneryRelation(
            self.__addDomainStringEntity(
                self.__addDomainStringEntity("", 'event', events), 
                'player', entities), 
            'beatat', beatat)
        return domainString

    def __addDomainStringEntity(self, inputString, entityName, entitySet):
        # Add relation for each entity
        for entity in entitySet:
            inputString = inputString + "{0} => {0}\n".format(entity)
        # Add entity set
        inputString = inputString + ("%s => {" % entityName)
        for entity in entitySet:
            inputString = inputString + "{0}, ".format(entity)
        inputString = inputString + "}\n"
        return inputString

    def _addDomainStringTreneryRelation(self, inputString, relationName, relationTriples):
        inputString = inputString + ("%s => {" % relationName)
        for (entity1, entity2, event) in relationTriples:
            inputString = inputString + "({0}, {1}, {2}), ".format(entity1, entity2, event)
        inputString = inputString + "}\n"
        return inputString