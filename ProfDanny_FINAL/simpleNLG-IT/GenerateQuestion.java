import simplenlg.features.italian.ItalianLexicalFeature;
import simplenlg.framework.*;
import simplenlg.lexicon.*;
import simplenlg.lexicon.italian.*;
import simplenlg.realiser.*;
import simplenlg.phrasespec.*;
import simplenlg.features.*;
import org.json.JSONObject;

public class GenerateQuestion {

    public static void main(String[] args) {
        String intType  = args[1];
        String text = args[0];

        JSONObject jo = new JSONObject(text);

        String subject_specifier = "";
        String subject = jo.getString("subject");
        if (subject.split(" ").length > 1) {
            subject_specifier = subject.split(" ")[0];
            subject = subject.split(" ")[1];
        }

        String object_specifier = "";
        String object = "";
        if (jo.has("object")){
            object = jo.getString("object");
            if (object.split(" ").length > 1) {
                object_specifier = object.split(" ")[0];
                object = object.split(" ")[1];
            }
        }


        String verb = "";
        if (jo.has("verb")) {
            verb = jo.getString("verb");
        }



        Lexicon italianLexicon = new ITXMLLexicon();
        NLGFactory factory = new NLGFactory(italianLexicon);
        Realiser realiser = new Realiser();
        String output = null;

        NPPhraseSpec np_subj = factory.createNounPhrase(subject_specifier, subject);
        if (jo.has("sagg")) {
            WordElement sagg = italianLexicon.getWord(jo.getString("sagg"), LexicalCategory.ADJECTIVE);
            np_subj.addModifier(sagg);

        }

        if (jo.has("scompl")) {
            np_subj.setComplement(jo.getString("scompl"));
        }
        if (jo.has("sgender") && jo.getString("sgender").equals("F")) {
            np_subj.setFeature(LexicalFeature.GENDER, Gender.FEMININE);
        }
        if (jo.has("splural") && jo.getString("splural").equals("T")) {
            np_subj.setFeature(Feature.NUMBER, NumberAgreement.PLURAL);
            np_subj.setPlural(true);
        }


        VPPhraseSpec vp = null;
        if (!verb.isEmpty())vp = factory.createVerbPhrase(verb);
        if (jo.has("vcompl")) {
            vp.setComplement(jo.getString("vcompl"));
        }
        NPPhraseSpec np_obj = null;
        if (!object.equals("")){


         np_obj = factory.createNounPhrase(object_specifier, object);
        if (jo.has("oagg")) {
            WordElement oagg = italianLexicon.getWord(jo.getString("oagg"), LexicalCategory.ADJECTIVE);
            np_obj.addModifier(oagg);
        }
        if (jo.has("ocompl")) {
            np_obj.setComplement(jo.getString("ocompl"));
        }
        if (jo.has("ogender") && jo.getString("ogender").equals("F")) {
            np_obj.setFeature(LexicalFeature.GENDER, Gender.FEMININE);
        }
        if (jo.has("oplural") && jo.getString("oplural").equals("T")) {
            np_obj.setFeature(Feature.NUMBER, NumberAgreement.PLURAL);
            np_obj.setPlural(true);
        }

        }

        SPhraseSpec proposition = factory.createClause(np_subj, vp, np_obj);

        if (subject.equals("noi")){
            proposition.setSubject("noi");
            proposition.setVerb(verb);
        }

        if (jo.has("tense")) {
            if (jo.getString("tense").equals("presente")) {
                proposition.setFeature(Feature.TENSE, Tense.PRESENT);
            }
            if (jo.getString("tense").equals("passato prossimo")) {
                proposition.setFeature(Feature.TENSE, Tense.PAST);
                proposition.setFeature(Feature.PERFECT, true);
            }
        }



        if (intType.equals("WHICH_SUBJECT")) {
            proposition.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.WHO_SUBJECT);
        }else if (intType.equals("WHAT_SUBJECT")) {
            proposition.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.WHO_SUBJECT);
        } else if ( intType.equals("WHICH_OBJECT")) {
            proposition.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.WHAT_OBJECT);
        } else {
            proposition.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.valueOf(intType));
        }

        if (jo.has("passive") && jo.getString("passive").equals("T")) {
            proposition.setFeature(Feature.PASSIVE, true);
        }

        if (jo.has("perfect") && jo.getString("perfect").equals("T")) proposition.setFeature(Feature.PERFECT, true);
        if (jo.has("auxessere") && jo.getString("auxessere").equals("T")) {
            proposition.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);
        }
        output = realiser.realiseSentence(proposition);

        if (intType.equals("WHICH_SUBJECT")) {
            output = output.replace("Chi", "Quale");
        } else if (intType.equals("WHAT_SUBJECT")) {
            output = output.replace("Chi", "Cosa");
            output = output.replace("chi", "cosa");
        } else if (intType.equals("WHICH_OBJECT")) {
            output = output.replace("Che cosa", "Quale");
        } else if (intType.equals("WHAT_OBJECT")) {
            output = output.replace("Che cosa", "Cosa");
        }

        System.out.println(output);

    }
}



