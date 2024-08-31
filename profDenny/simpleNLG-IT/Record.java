import simplenlg.features.*;
import simplenlg.framework.*;
import simplenlg.features.italian.*;
import java.util.List;
import java.util.ArrayList;
import simplenlg.realiser.Realiser;
import simplenlg.lexicon.italian.ITXMLLexicon;
import simplenlg.lexicon.Lexicon;
import simplenlg.framework.NLGFactory;

import simplenlg.features.*;
import simplenlg.framework.*;
import simplenlg.phrasespec.*;
import simplenlg.lexicon.Lexicon;

class Record {
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

    public List<String> getWords() {
        return words;
    }

    public void setWords(List<String> words) {
        this.words = words;
    }

    public List<List<String>> getOut_context() {
        return out_context;
    }

    public void setOut_context(List<List<String>> out_context) {
        this.out_context = out_context;
    }

    public List<Boolean> getMissing_dep() {
        return missing_dep;
    }

    public void setMissing_dep(List<Boolean> missing_dep) {
        this.missing_dep = missing_dep;
    }

    public List<Float> getScore() {
        return score;
    }

    public void setScore(List<Float> score) {
        this.score = score;
    }

    public Boolean getMisspells() {
        return misspells;
    }

    public void setMisspells(Boolean misspells) {
        this.misspells = misspells;
    }

    public Boolean isFullCorrect() {
        return score.get(0) == 1.0f;
    }

    public Boolean isFullWrong() {
        return score.get(0) == 0.0f;
    }

    public Boolean isMisspells() {
        return misspells;
    }

    public Boolean isMissingDepSix() {
        Boolean misspell =false;
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.6f && missing_dep.get(i)) {
                misspell = true;
                break;
            }
        }
        return misspell;
    }

    public Boolean isMissingDepTwo() {
        Boolean misspell =false;
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.2f && missing_dep.get(i)) {
                misspell = true;
                break;
            }
        }
        return misspell;
    }

    public Boolean isMissingDepZero() {
        Boolean misspell =false;
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.0f && missing_dep.get(i)) {
                misspell = true;
                break;
            }
        }
        return misspell;
    }

    public List<String> partialSixScore(){
        List<String> partial = new ArrayList<>();
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.6f) {
                partial.add(words.get(i));
            }
        }
        return partial;
    }

    public List<String> partialTwoScore(){
        List<String> partial = new ArrayList<>();
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.2f) {
                partial.add(words.get(i));
            }
        }
        return partial;
    }

    public List<String> partialZeroScore(){
        List<String> partial = new ArrayList<>();
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.0f) {
                partial.add(words.get(i));
            }
        }
        return partial;
    }

    public List<String> outOfContext(){
        return out_context.get(0);
    }

    public List<String> outOfContextSix(){
        List<String> words = new ArrayList<>();
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.6f) {
                words.addAll(out_context.get(i));
            }
        }
        return words;
    }

    public List<String> outOfContextTwo(){
        List<String> words = new ArrayList<>();
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.2f) {
                words.addAll(out_context.get(i));
            }
        }
        return words;
    }

    public List<String> outOfContextZero(){
        List<String> words = new ArrayList<>();
        for (int i = 1; i < score.size() ; i++) {
            if (score.get(i) == 0.0f) {
                words.addAll(out_context.get(i));
            }
        }
        return words;
    }

     public static void main(String[] args) {

        Record record1 = new Record(
                List.of("PCFG", "grammatica", "regole","probabilità"),
                List.of(new ArrayList<>(),List.of("ciao"),new ArrayList<>(),new ArrayList<>() ),
                List.of(false, true, false, false),
                List.of(0.6f, 0.6f, 0.2f, 0.0f),
                true
        );

        List<Record> records = new ArrayList<>();
        records.add(record1);


        Lexicon lexIta = new ITXMLLexicon();

        NLGFactory factory = new NLGFactory(lexIta);

        Realiser realiser = new Realiser();

        String output = "";

        
        for(int j = 0; j < records.size(); j++){
        Record record = records.get(j);
        if(record.isFullCorrect()) {
            SPhraseSpec mainClause = factory.createClause();
            mainClause.setSubject("tu");
            mainClause.setVerb("rispondere");
            mainClause.setFeature(Feature.TENSE, Tense.PAST);
            mainClause.setFeature(Feature.PERFECT, true);
            mainClause.addComplement("in maniera precisa e completa");
            mainClause.addFrontModifier("Riguardo " + record.getWords().get(0));
            
            SPhraseSpec complementClause = factory.createClause();
            complementClause.setVerb("ottenere");
            complementClause.setFeature(Feature.FORM, Form.GERUND);
            complementClause.setFeature(Feature.TENSE, Tense.PRESENT);
            complementClause.setObject("il punteggio massimo");
            
            CoordinatedPhraseElement cord = factory.createCoordinatedPhrase();

            cord.addCoordinate(mainClause);
            cord.addCoordinate(complementClause);
            cord.setConjunction("");

            output += realiser.realiseSentence(cord) + "😎 👌 🔥 💯 🤑\n";
        }else if(record.isFullWrong()) {
            SPhraseSpec mainClause = factory.createClause();
            mainClause.setSubject("tu");
            mainClause.setVerb("rispondere");
            mainClause.setFeature(Feature.TENSE, Tense.PAST);
            mainClause.setFeature(Feature.PERFECT, true);
            mainClause.addComplement("in maniera completamente errata");
            mainClause.addFrontModifier("Riguardo " + record.getWords().get(0));
            
            CoordinatedPhraseElement cord = factory.createCoordinatedPhrase();

            SPhraseSpec complementClause = factory.createClause();
            complementClause.setVerb("ottenere");
            complementClause.setFeature(Feature.FORM, Form.GERUND);
            complementClause.setFeature(Feature.TENSE, Tense.PRESENT);
            complementClause.setObject("punteggio minimo");

            cord.addCoordinate(mainClause);
            cord.addCoordinate(complementClause);
            cord.setConjunction("");
            output += realiser.realiseSentence(cord) + "❌ 😨 🚽 😡 \n";
        }else{
            List<String> partialSixScore = record.partialSixScore();
            if (!partialSixScore.isEmpty()) {
                SPhraseSpec mainClause = factory.createClause();
                mainClause.setSubject("tu");
                mainClause.setVerb("parlare");
                CoordinatedPhraseElement obj = factory.createCoordinatedPhrase();
                for (int i = 0; i < partialSixScore.size(); i++) {
                    if (i == 0) {
                        obj.addCoordinate("di " + partialSixScore.get(i));
                    } else {
                        obj.addCoordinate(partialSixScore.get(i));
                    }
                }

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
                output += realiser.realiseSentence(coordinatedPhrase) + "\n";

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
                output += realiser.realiseSentence(finalClause)+ "\n";
            }
            List<String> partialSixScoreOutOfContext = record.outOfContextSix();
            if (!partialSixScoreOutOfContext.isEmpty()) {
                SPhraseSpec firstClause = factory.createClause();
                firstClause.setSubject("tu");
                firstClause.setVerb("andare");
                firstClause.setComplement("fuori contesto");

                CoordinatedPhraseElement obj = factory.createCoordinatedPhrase();
                for (int i = 0; i < partialSixScoreOutOfContext.size(); i++) {
                    if (i == 0) {
                        obj.addCoordinate("parlandomi di " + partialSixScoreOutOfContext.get(i));
                    }  else {
                        obj.addCoordinate(partialSixScoreOutOfContext.get(i));
                    }
                }
                firstClause.setObject(obj);


                // Seconda frase
                SPhraseSpec secondClause = factory.createClause();
                secondClause.setVerb("aggravare");
                secondClause.setObject("la tua situazione");
                secondClause.setFeature(Feature.FORM, Form.GERUND);
                secondClause.setFeature(Feature.TENSE, Tense.PRESENT);

                CoordinatedPhraseElement coordinatedPhrase = factory.createCoordinatedPhrase();
                coordinatedPhrase.addCoordinate(firstClause);
                coordinatedPhrase.addCoordinate(secondClause);
                coordinatedPhrase.setConjunction("");

                output += realiser.realiseSentence(coordinatedPhrase) + "\n\n";
            }
            if (record.isMissingDepSix()) {
                // Inoltre non sei stato molto preciso
                SPhraseSpec firstClause = factory.createClause();
                firstClause.setSubject("tu");
                firstClause.setVerb("essere");
                firstClause.setComplement("impreciso");
                firstClause.setFeature(Feature.TENSE, Tense.PAST);
                firstClause.setFeature(Feature.PERFECT, true);
                firstClause.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);
                firstClause.addFrontModifier("Inoltre");

                output += realiser.realiseSentence(firstClause) + "\n";
            }
            List<String> partialTwoScore = record.partialTwoScore();
            if (!partialTwoScore.isEmpty()) {
                SPhraseSpec mainClause = factory.createClause();
                mainClause.setSubject("la tua risposta");
                mainClause.setVerb("avere");
                mainClause.addComplement("molte lacune");

                NPPhraseSpec questiPunti = factory.createNounPhrase("questo", "punto");
                questiPunti.setPlural(partialTwoScore.size() > 1);
                PPPhraseSpec complement = factory.createPrepositionPhrase("su", questiPunti);
                mainClause.setObject(complement);

                CoordinatedPhraseElement points = factory.createCoordinatedPhrase();
                for (int i = 0; i < partialTwoScore.size(); i++) {
                    points.addCoordinate(partialTwoScore.get(i));
                }
                mainClause.addComplement(points);
                
                output += realiser.realiseSentence(mainClause) + "\n";
            }
            List<String> partialTwoScoreOutOfContext = record.outOfContextTwo();
            if (!partialTwoScoreOutOfContext.isEmpty()) {
                SPhraseSpec firstClause = factory.createClause();
                firstClause.setSubject("tu");
                firstClause.setVerb("andare");
                firstClause.setComplement("fuori contesto");

                CoordinatedPhraseElement obj = factory.createCoordinatedPhrase();
                for (int i = 0; i < partialTwoScoreOutOfContext.size(); i++) {
                    if (i == 0) {
                        obj.addCoordinate("parlandomi di " + partialTwoScoreOutOfContext.get(i));
                    }  else {
                        obj.addCoordinate(partialTwoScoreOutOfContext.get(i));
                    }
                }
                firstClause.setObject(obj);

                // Seconda frase
                SPhraseSpec secondClause = factory.createClause();
                secondClause.setVerb("aggravare");
                secondClause.setObject("la tua situazione");
                secondClause.setFeature(Feature.FORM, Form.GERUND);
                secondClause.setFeature(Feature.TENSE, Tense.PRESENT);

                CoordinatedPhraseElement coordinatedPhrase = factory.createCoordinatedPhrase();
                coordinatedPhrase.addCoordinate(firstClause);
                coordinatedPhrase.addCoordinate(secondClause);
                coordinatedPhrase.setConjunction("");

                output += realiser.realiseSentence(coordinatedPhrase) + "\n";
            }
            if (record.isMissingDepTwo()) {
                // Inoltre non sei stato molto preciso
                SPhraseSpec firstClause = factory.createClause();
                firstClause.setSubject("tu");
                firstClause.setVerb("essere");
                firstClause.setComplement("impreciso");
                firstClause.setFeature(Feature.TENSE, Tense.PAST);
                firstClause.setFeature(Feature.PERFECT, true);
                firstClause.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);
                firstClause.addFrontModifier("Inoltre");

                output += realiser.realiseSentence(firstClause) + "\n";
            }
            List<String> partialZeroScore = record.partialZeroScore();
            if (!partialZeroScore.isEmpty()) {
                SPhraseSpec mainClause = factory.createClause();
                mainClause.setSubject("tu");
                mainClause.setVerb("parlare");
                CoordinatedPhraseElement obj = factory.createCoordinatedPhrase();
                for(int i = 0; i < partialZeroScore.size(); i++) {
                    if (i == 0) {
                        obj.addCoordinate("di " + partialZeroScore.get(i));
                    }  else {
                        obj.addCoordinate(partialZeroScore.get(i));
                    }
                }
                mainClause.setObject(obj);
                mainClause.addFrontModifier("Nella tua risposta");
                mainClause.setFeature(Feature.TENSE, Tense.PAST);
                mainClause.setFeature(Feature.PERFECT, true);
                mainClause.setFeature(Feature.NEGATED, true);

                // Frase subordinata
                SPhraseSpec subClause = factory.createClause();
                subClause.setSubject("tu");
                subClause.setVerb("essere");
                subClause.setObject("penalizzato");
                subClause.setFeature(Feature.TENSE, Tense.PAST);
                subClause.setFeature(Feature.PERFECT, true);

                // Coordinare le frasi
                CoordinatedPhraseElement coordinatedPhrase = factory.createCoordinatedPhrase();
                coordinatedPhrase.addCoordinate(mainClause);
                coordinatedPhrase.addCoordinate(subClause);
                coordinatedPhrase.setConjunction("perciò");

                // Realizzare la frase finale
                output += realiser.realiseSentence(coordinatedPhrase) + "😅😅😅\n";
            }
            List<String> partialZeroScoreOutOfContext = record.outOfContextZero();
            if (!partialZeroScoreOutOfContext.isEmpty()) {
                SPhraseSpec firstClause = factory.createClause();
                firstClause.setSubject("tu");
                firstClause.setVerb("andare");
                firstClause.setComplement("fuori contesto");

                CoordinatedPhraseElement obj = factory.createCoordinatedPhrase();
                for (int i = 0; i < partialZeroScoreOutOfContext.size(); i++) {
                    if (i == 0) {
                        obj.addCoordinate("parlandomi di " + partialZeroScoreOutOfContext.get(i));
                    }  else {
                        obj.addCoordinate(partialZeroScoreOutOfContext.get(i));
                    }
                }
                firstClause.setObject(obj);

                // Seconda frase
                SPhraseSpec secondClause = factory.createClause();
                secondClause.setVerb("aggravare");
                secondClause.setObject("la tua situazione");
                secondClause.setFeature(Feature.FORM, Form.GERUND);
                secondClause.setFeature(Feature.TENSE, Tense.PRESENT);

                CoordinatedPhraseElement coordinatedPhrase = factory.createCoordinatedPhrase();
                coordinatedPhrase.addCoordinate(firstClause);
                coordinatedPhrase.addCoordinate(secondClause);
                coordinatedPhrase.setConjunction("");

                output += realiser.realiseSentence(coordinatedPhrase) + "❓🤔❓\n";
                
            }
            if (record.isMissingDepZero()) {
                SPhraseSpec firstClause = factory.createClause();
                firstClause.setSubject("tu");
                firstClause.setVerb("essere");
                firstClause.setComplement("impreciso");
                firstClause.setFeature(Feature.TENSE, Tense.PAST);
                firstClause.setFeature(Feature.PERFECT, true);
                firstClause.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);
                firstClause.addFrontModifier("Inoltre");

                output += realiser.realiseSentence(firstClause) + "🔍🕵🔍\n";
            }
            if(record.isMisspells()) {
                SPhraseSpec mainClause = factory.createClause();
        
                NPPhraseSpec nelleTueRisposte = factory.createNounPhrase("nelle", "tue risposte" );
                nelleTueRisposte.setPlural(true);
                mainClause.setSubject(nelleTueRisposte);
                mainClause.setVerb("essere");
                
                NPPhraseSpec questiPunti = factory.createNounPhrase("presente" );
                questiPunti.setPlural(true);
                mainClause.addComplement(questiPunti);
                mainClause.setFeature(Feature.TENSE, Tense.PAST);
                mainClause.setFeature(ItalianLexicalFeature.AUXILIARY_ESSERE, true);    
                mainClause.setObject("errori grammaticali");
                output += realiser.realiseSentence(mainClause) + "🔠 ✍🏻 👽\n";
            }
        }
    
    SPhraseSpec mainClause1 = factory.createClause();
    mainClause1.setSubject("tu");
    mainClause1.setVerb("prendere");
    mainClause1.setObject(record.getScore().get(0) * (30/records.size())  + "/" +  30/records.size());
    
    mainClause1.setComplement("per l'argomento " + record.getWords().get(0));
    mainClause1.setFeature(Feature.TENSE, Tense.PAST);
    mainClause1.setFeature(Feature.PERFECT, true);
    
    SPhraseSpec mainClause2 = factory.createClause();
    mainClause2.setVerb("considerare");
    mainClause2.setFeature(Feature.FORM, Form.GERUND);
    
    SPhraseSpec mainClause3 = factory.createClause();
    mainClause3.setSubject("io");
    mainClause3.setVerb("dire");
    mainClause3.addComplement("precedentemente");
    mainClause3.setFeature(Feature.TENSE, Tense.PAST);
    mainClause3.setFeature(Feature.PERFECT, true);
    mainClause2.setComplement("ciò");
    mainClause2.setComplement(mainClause3);

    CoordinatedPhraseElement cord5 = factory.createCoordinatedPhrase();
    cord5.addCoordinate(mainClause2);
    cord5.addCoordinate(mainClause1);
    cord5.setConjunction("");
    output += "\n" + realiser.realiseSentence(cord5);
    System.out.println(output);
    }
}

}
