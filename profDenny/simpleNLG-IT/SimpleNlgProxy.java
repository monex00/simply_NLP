import simplenlg.framework.*;
import simplenlg.lexicon.*;
import simplenlg.lexicon.italian.*;
import simplenlg.realiser.*;
import simplenlg.phrasespec.*;
import simplenlg.features.*;

//args : subject, verb, object, interrogativeType
public class SimpleNlgProxy {
    public static void main(String[] args) {
		String subject = args[0];
		String verb = args[1];
		String object = args[2];
		String interrogativeType = args[3];
		String tense = args[4];

        // Create an NLGFactory and a language lexicon
        Lexicon lexicon = new ITXMLLexicon();
		NLGFactory factory = new NLGFactory(lexicon);
        Realiser realiser = new Realiser();
		//realiser.setDebugMode(true);
		String output = null;


		//create nouns
		String [] splitted_subject = subject.split(" ");
		NPPhraseSpec np_subj = splitted_subject > 1 ? factory.createNounPhrase(splitted_subject[0], splitted_subject[1]) : factory.createNounPhrase(subject);
		String [] splitted_object = subject.split(" ");
		NPPhraseSpec np_obj = splitted_object > 1 ? factory.createNounPhrase(splitted_object[0], splitted_object[1]) : factory.createNounPhrase(object);
		
		//create clause
		SPhraseSpec clauseIt = italianFactory.createClause(np_subj, verb, np_obj);

        //add features to clause
		clauseIt.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.valueOf(args[3]));
		clauseIt.setFeature(Feature.FORM, Form.NORMAL);
		clauseIt.setFeature(Feature.TENSE, Tense.PRESENT);

        //set tense based on the input tense argument
		if(tense == "passato prossimo"){
			clauseIt.setFeature(Feature.PERFECT, true);
		}

		//realization
		output = realiser.realiseSentence(clauseIt);
		System.out.print(output);
    }
}
