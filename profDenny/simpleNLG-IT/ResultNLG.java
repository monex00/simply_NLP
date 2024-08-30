import simplenlg.features.*;
import simplenlg.framework.NLGFactory;
import simplenlg.lexicon.Lexicon;
import simplenlg.lexicon.italian.ITXMLLexicon;
import simplenlg.phrasespec.NPPhraseSpec;
import simplenlg.phrasespec.SPhraseSpec;
import simplenlg.phrasespec.VPPhraseSpec;
import simplenlg.realiser.Realiser;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import simplenlg.features.*;
        import simplenlg.framework.*;
        import simplenlg.phrasespec.*;
        import simplenlg.lexicon.Lexicon;

//ITALIAN
//importo feature italiane
import simplenlg.features.italian.*;
//importo lessico italiano
        import simplenlg.lexicon.italian.*;
//importo il realizer francese che richiama i metodi
//realiseSyntax e realiseMorphology degli elementi linguistici
        import simplenlg.realiser.Realiser;
/* class Record {
    private List<String> words;
    private List<List<String>> out_context;
    private List<Boolean> missing_dep;
    private List<Float> score;

    private Boolean misspells;

    public Record(List<String> words,List<List<String>> out_context,List<Boolean> missing_dep,List<Float> score,Boolean misspells) {
        this.words = words;
        this.out_context = out_context;
        this.missing_dep = missing_dep;
        this.score = score;
        this.misspells = misspells;
    }

    public Boolean isFullCorrect() {
        return score.getFirst() == 1.0;
    }

    public Boolean isFullWrong() {
        return score.getFirst() == 0.0;
    }

    public Boolean isMisspells() {
        return misspells;
    }

    public List<String> partialSixScore(){
        List<String> partialSixScore = new ArrayList<>();
        for (int i = 0; i < score.size() ; i++) {
            if (score.get(i) == 0.6) {
                partialSixScore.add(words.get(i));
            }
        }
        return partialSixScore;
    }

    public List<String> partialTwoScore(){
        List<String> partialSixScore = new ArrayList<>();
        for (int i = 0; i < score.size() ; i++) {
            if (score.get(i) == 0.2) {
                partialSixScore.add(words.get(i));
            }
        }
        return partialSixScore;
    }

    public List<String> outOfContext(){
        return out_context.getFirst();
    }

    public List<String> outOfContextSix(){
        List<String> words = new ArrayList<>();
        for (int i = 0; i < score.size() ; i++) {
            if (score.get(i) == 0.6) {
                words.addAll(out_context.get(i));
            }
        }
        return words;
    }

    public List<String> outOfContextTwo(){
        List<String> words = new ArrayList<>();
        for (int i = 0; i < score.size() ; i++) {
            if (score.get(i) == 0.2) {
                words.addAll(out_context.get(i));
            }
        }
        return words;
    }

} */

public class ResultNLG {

    public static void main(String[] args) {
        //--------------------------
        // RISPOSTA COMPLETAMENTE ESATTA
        // Riguardo a questo argomento x, hai risposto in maniera precisa e completa ottenendo il punteggio masssimo

        // RISPOSTA COMPLETAMENTE ESATTA
        // riguardo a questo argomento hai risposto in maniera precisa e coimpleta quindi hai ottenuto il punteggio massimo

        // RISPOSTA PARZIALMENTE ESATTA 0.6
        // Nella tua risposta mi hai parlato di { } solo dopo che ti ho fatto ulteriori domande, per questo sei stato penalizzato nel punteggio
   
        // RISPOSTA PARZIALMENTE ESATTA 0.2
        // La tua preparazione ha molte lacune su questi punti grammatica, regole e probabilità.
        
        // OUT OF CONTEXT
        // Sei andato fuori contesto parlandomi di {} quesWto ha aggravato la tua situazione

        // MISSPEL
        // Inoltre nelle tue risposte erano presenti errori grammaticali

        // PUNTEGGIO FINALE RISPOSTA - NO CON RISPOSTA COMPLETA ESATTA - NO CON RISPOSTA COMPLETAMENTE ERRATA
        // considerando ciò che ho detto precedentemente hai preso questo punteggio per questo argomento {}

        // RISPOSTA COMPLETAMENTE ERRATA
        // Riguardo a questo argomento x, hai risposto in maniera completamente errata ottenendo punteggio zero
        //-------------------------

        //Complessivamente hai totalizzato 28/30 punti 

        // RISPOSTA PARZIALMENTE ESATTA 0.6
        Lexicon lexIta = new ITXMLLexicon();
        
        NLGFactory factory = new NLGFactory(lexIta);
        
        Realiser realiser = new Realiser();
        
        SPhraseSpec mainClause = factory.createClause();
        mainClause.setSubject("tu");
        mainClause.setVerb("parlare");
        CoordinatedPhraseElement obj = factory.createCoordinatedPhrase();
        obj.addCoordinate("di grammatica");
        obj.addCoordinate("regole");
        obj.addCoordinate("probabilità");
        mainClause.setObject(obj);
        mainClause.addFrontModifier("Nella tua risposta");
        mainClause.setFeature(Feature.TENSE, Tense.PAST);
        mainClause.setFeature(Feature.PERFECT, true);

        // Frase subordinata
        SPhraseSpec subClause = factory.createClause();
        subClause.setSubject("io");
        subClause.setVerb("fare");
        subClause.setObject("ulteriori domande");
        subClause.setFeature(Feature.TENSE, Tense.PAST);
        subClause.setFeature(Feature.PERFECT, true);

        // Coordinare le frasi
        CoordinatedPhraseElement coordinatedPhrase = factory.createCoordinatedPhrase();
        coordinatedPhrase.addCoordinate(mainClause);
        coordinatedPhrase.addCoordinate(subClause);
        coordinatedPhrase.setConjunction(" ma solo dopo che");

        // Realizzare la frase coordinata
        String output = realiser.realiseSentence(coordinatedPhrase);
        System.out.println(output);

        // Frase finale
        SPhraseSpec finalClause = factory.createClause();
        finalClause.setSubject("tu");
        finalClause.setVerb("essere");
        finalClause.setComplement("penalizzato");
        finalClause.setObject("nel punteggio");
        finalClause.setFeature(Feature.TENSE, Tense.PAST);
        finalClause.setFeature(Feature.PERFECT, true);
        finalClause.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);
        finalClause.addFrontModifier("Per questo motivo");

        // Realizzare la frase finale
        output = realiser.realiseSentence(finalClause);
        System.out.println(output);

        
        // OUT OF CONTEXT
        SPhraseSpec firstClause1 = factory.createClause();
        firstClause1.setSubject("tu");
        firstClause1.setVerb("andare");
        firstClause1.setComplement("fuori contesto");
        firstClause1.setObject("parlandomi di dinamica");
        firstClause1.addFrontModifier("Inoltre");

        
        // Seconda frase
        SPhraseSpec secondClause1 = factory.createClause();
        secondClause1.setVerb("aggravare");
        secondClause1.setObject("la tua situazione");
        secondClause1.setFeature(Feature.FORM, Form.GERUND);
        secondClause1.setFeature(Feature.TENSE, Tense.PRESENT);

        CoordinatedPhraseElement coordinatedPhrase1 = factory.createCoordinatedPhrase();
        coordinatedPhrase1.addCoordinate(firstClause1);
        coordinatedPhrase1.addCoordinate(secondClause1);
        coordinatedPhrase1.setConjunction("");

        output = realiser.realiseSentence(coordinatedPhrase1);
        System.out.println(output);

        // 0.2 QUESTION
        // Frase principale
        SPhraseSpec mainClause2 = factory.createClause();
        mainClause2.setSubject("la tua risposta");
        mainClause2.setVerb("avere");
        mainClause2.addComplement("molte lacune");



        NPPhraseSpec questiPunti = factory.createNounPhrase("questo", "punto");
		questiPunti.setPlural(true);
        PPPhraseSpec complement = factory.createPrepositionPhrase("su", questiPunti);
        mainClause2.setObject(complement);

        // Creare la lista dei punti
        CoordinatedPhraseElement points1 = factory.createCoordinatedPhrase();
        points1.addCoordinate("grammatica");
        points1.addCoordinate("regole");
        points1.addCoordinate("probabilità");
        
        // Aggiungere i punti come complemento
        mainClause2.addComplement(points1);
        
        // Realizzare la frase
        output = realiser.realiseSentence(mainClause2);
        System.out.println(output);

        // RISPOSTA CORRETTA  Riguardo a questo argomento x, hai risposto in maniera precisa e completa ottenendo il punteggio masssimo
        SPhraseSpec mainClause3 = factory.createClause();
        mainClause3.setSubject("tu");
        mainClause3.setVerb("rispondere");
        mainClause3.setFeature(Feature.TENSE, Tense.PAST);
        mainClause3.setFeature(Feature.PERFECT, true);
        mainClause3.addComplement("in maniera precisa e completa");
        // Aggiungere il front modifier "Riguardo a questo argomento NLG"
        mainClause3.addFrontModifier("Riguardo NLG");
        
        // Aggiungere il complemento "ottenendo il punteggio massimo"
        CoordinatedPhraseElement cord2 = factory.createCoordinatedPhrase();

        SPhraseSpec complementClause = factory.createClause();
        complementClause.setVerb("ottenere");
        complementClause.setFeature(Feature.FORM, Form.GERUND);
        complementClause.setFeature(Feature.TENSE, Tense.PRESENT);
        complementClause.setObject("il punteggio massimo");

        cord2.addCoordinate(mainClause3);
        cord2.addCoordinate(complementClause);
        cord2.setConjunction("");

        // Realizzare la frase
        output = realiser.realiseSentence(cord2);
        System.out.println(output);

        // RISPOSTA COMPLETELY WRONG - Riguardo a  x, hai risposto in maniera completamente errata ottenendo punteggio zero
        SPhraseSpec mainClause4 = factory.createClause();
        mainClause4.setSubject("tu");
        mainClause4.setVerb("rispondere");
        mainClause4.setFeature(Feature.TENSE, Tense.PAST);
        mainClause4.setFeature(Feature.PERFECT, true);
        mainClause4.addComplement("in maniera completamente errata");
        // Aggiungere il front modifier "Riguardo a questo argomento NLG"
        mainClause4.addFrontModifier("Riguardo NLG");
        
        // Aggiungere il complemento "ottenendo il punteggio massimo"
        CoordinatedPhraseElement cord3 = factory.createCoordinatedPhrase();

        SPhraseSpec complementClause1 = factory.createClause();
        complementClause1.setVerb("ottenere");
        complementClause1.setFeature(Feature.FORM, Form.GERUND);
        complementClause1.setFeature(Feature.TENSE, Tense.PRESENT);
        complementClause1.setObject("punteggio minimo");

        cord3.addCoordinate(mainClause4);
        cord3.addCoordinate(complementClause1);
        cord3.setConjunction("");

        // Realizzare la frase
        output = realiser.realiseSentence(cord3);
        System.out.println(output);


        // MISSPELL - Inoltre nelle tue risposte erano presenti errori grammaticali
        SPhraseSpec mainClause5 = factory.createClause();
        
        NPPhraseSpec questiPunti2 = factory.createNounPhrase("nelle", "tue risposte" );
		questiPunti2.setPlural(true);
        mainClause5.setSubject(questiPunti2);
        mainClause5.setVerb("essere");
        
        NPPhraseSpec questiPunti1 = factory.createNounPhrase("presente" );
		questiPunti1.setPlural(true);
        mainClause5.addComplement(questiPunti1);
        mainClause5.setFeature(Feature.TENSE, Tense.PAST);
        mainClause5.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);    
        mainClause5.setObject("errori grammaticali");

        
        
        // Aggiungere il front modifier "Inoltre"
        mainClause5.addFrontModifier("Inoltre");
        
        // Realizzare la frase
        output = realiser.realiseSentence(mainClause5);
        System.out.println(output);

        // PUNTEGGIO FINALE RISPOSTA - NO CON RISPOSTA COMPLETA ESATTA - NO CON RISPOSTA COMPLETAMENTE ERRATA
        // considerando ciò che ho detto precedentemente hai preso questo punteggio per questo argomento {}

        SPhraseSpec mainClause6 = factory.createClause();
        mainClause6.setSubject("tu");
        mainClause6.setVerb("prendere");
        mainClause6.setObject("8/10 punti");
        mainClause6.setComplement("per l'argomento NLG");
        mainClause6.setFeature(Feature.TENSE, Tense.PAST);
        mainClause6.setFeature(Feature.PERFECT, true);
        

        SPhraseSpec mainClause8 = factory.createClause();
        mainClause8.setVerb("considerare");
        mainClause8.setFeature(Feature.FORM, Form.GERUND);
        
        SPhraseSpec mainClause7 = factory.createClause();
        mainClause7.setSubject("io");
        mainClause7.setVerb("dire");
        mainClause7.addComplement("precedentemente");
        mainClause7.setFeature(Feature.TENSE, Tense.PAST);
        mainClause7.setFeature(Feature.PERFECT, true);

        // CoordinatedPhraseElement cord4 = factory.createCoordinatedPhrase();
        // cord4.addCoordinate(mainClause8);
        // cord4.addCoordinate(mainClause7);
        // cord4.setConjunction("ciò che");


        mainClause8.setComplement("ciò");
        mainClause8.setComplement(mainClause7);

        CoordinatedPhraseElement cord5 = factory.createCoordinatedPhrase();
        cord5.addCoordinate(mainClause8);
        cord5.addCoordinate(mainClause6);
        cord5.setConjunction("");
        // Add the prepositional phrase
        // PPPhraseSpec perQuestoArgomento = factory.createPrepositionPhrase("per", "l`argomento NLG");
        // mainClause6.addPostModifier(perQuestoArgomento);
        
        // Create the front modifier
        //PPPhraseSpec considerando = factory.createPrepositionPhrase("considerando", "ciò che ho detto precedentemente");
        //mainClause6.addFrontModifier(considerando);
        
        // Realize the sentence
        output = realiser.realiseSentence(cord5);
        System.out.println(output);
        

    }

}


