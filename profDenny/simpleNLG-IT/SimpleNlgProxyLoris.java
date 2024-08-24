//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
import java.util.ArrayList;
import java.util.List;
import java.util.HashMap;
import java.util.Map;
import simplenlg.framework.*;
import simplenlg.lexicon.*;
import simplenlg.lexicon.italian.*;
import simplenlg.realiser.*;
import simplenlg.phrasespec.*;
import simplenlg.features.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SimpleNlgProxyLoris {

    public static List<Word> parseText(String text) {
        List<Word> words = new ArrayList<>();
        String[] lines = text.split("\n");
        for (String line : lines) {
            if (line.startsWith("#") || line.trim().isEmpty()) {
                continue;
            }
            String[] columns = line.split("\t");
            // System.out.println("\n\n\n" + columns[0]);
            int id = Integer.parseInt(columns[0]);
            String form = columns[1];
            String lemma = columns[2];
            String upos = columns[3];
            String xpos = columns[4];
            String feats = columns[5];
            int head = Integer.parseInt(columns[6]);
            String deprel = columns[7];
            String deps = columns[8];
            String misc = columns[9];
            Word word = new Word(id, form, lemma, upos, xpos, feats, head, deprel, deps, misc);
            words.add(word);
        }
        return words;
    }

    public static DependencyTree buildTree(List<Word> words) {
        Map<Integer, DependencyTree> nodes = new HashMap<>();
        DependencyTree root = null;

        for (Word word : words) {
            DependencyTree node = new DependencyTree(word);
            nodes.put(word.id, node);
            if (word.head == 0) {
                root = node;
            }
        }

        for (Word word : words) {
            if (word.head != 0) {
                DependencyTree parent = nodes.get(word.head);
                parent.addChild(nodes.get(word.id));
            }
        }

        return root;
    }


    public static String udpipeApi(String text) {
         try {
            // Encode del testo per l'inclusione nell'URL
            String encodedText = URLEncoder.encode(text, "UTF-8");
            
            // Costruzione dell'URL
            String baseUrl = "http://lindat.mff.cuni.cz/services/udpipe/api/process?tokenizer&tagger&parser&model=italian-isdt-ud-2.12-230717&data=";
            String fullUrl = baseUrl + encodedText;

            // Creazione dell'oggetto URL
            URL url = new URL(fullUrl);

            // Apertura della connessione
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");

            // Lettura della risposta
            BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            String inputLine;
            StringBuilder content = new StringBuilder();

            while ((inputLine = in.readLine()) != null) {
                content.append(inputLine);
            }

            // Chiusura delle risorse
            in.close();
            connection.disconnect();

            return content.toString();

        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) {
        String intType  = args[1];
        String text = udpipeApi(args[0]);
        String regex = "\"result\"\\s*:\\s*\"([^\"]*)\"";
        
        Pattern pattern = Pattern.compile(regex);
        
        Matcher matcher = pattern.matcher(text);
        if (matcher.find()) {
            text = matcher.group(1).replace("\\n", "\n").replace("\\t", "\t");
        } else {
            System.out.println("NULL");
        }


        if(text == null) {
            System.out.println("NULL");
            return;
        }
/* 
        String text = "# generator = UDPipe 2, https://lindat.mff.cuni.cz/services/udpipe\n" +
                "# udpipe_model = italian-isdt-ud-2.12-230717\n" +
                "# udpipe_model_licence = CC BY-NC-SA\n" +
                "# newdoc\n" +
                "# newpar\n" +
                "# sent_id = 1\n" +
                "# text = ogni regola ha associata una probabilità\n" +
                "1\togni\togni\tDET\tDI\tNumber=Sing|PronType=Ind\t2\tdet\t_\tTokenRange=0:4\n" +
                "2\tregola\tregola\tNOUN\tS\tGender=Fem|Number=Sing\t4\tnsubj\t_\tTokenRange=5:11\n" +
                "3\tha\tavere\tAUX\tVA\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin\t4\taux\t_\tTokenRange=12:14\n" +
                "4\tassociata\tassociare\tVERB\tV\tGender=Fem|Number=Sing|Tense=Past|VerbForm=Part\t0\troot\t_\tTokenRange=15:24\n" +
                "5\tuna\tuno\tDET\tRI\tDefinite=Ind|Gender=Fem|Number=Sing|PronType=Art\t6\tdet\t_\tTokenRange=25:28\n" +
                "6\tprobabilità\tprobabilità\tNOUN\tS\tGender=Fem\t4\tobj\t_\tSpaceAfter=No|TokenRange=29:40";


        String text2 = "# generator = UDPipe 2, https://lindat.mff.cuni.cz/services/udpipe\n" +
                "# udpipe_model = italian-isdt-ud-2.12-230717\n" +
                "# udpipe_model_licence = CC BY-NC-SA\n" +
                "# newdoc\n" +
                "# newpar\n" +
                "# sent_id = 1\n" +
                "# text = le regole caratterizzano una grammatica\n" +
                "1\tle\til\tDET\tRD\tDefinite=Def|Gender=Fem|Number=Plur|PronType=Art\t2\tdet\t_\tTokenRange=0:2\n" +
                "2\tregole\tregola\tNOUN\tS\tGender=Fem|Number=Plur\t3\tnsubj\t_\tTokenRange=3:9\n" +
                "3\tcaratterizzano\tcaratterizzare\tVERB\tV\tMood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin\t0\troot\t_\tTokenRange=10:24\n" +
                "4\tuna\tuno\tDET\tRI\tDefinite=Ind|Gender=Fem|Number=Sing|PronType=Art\t5\tdet\t_\tTokenRange=25:28\n" +
                "5\tgrammatica\tgrammatica\tNOUN\tS\tGender=Fem|Number=Sing\t3\tobj\t_\tSpaceAfter=No|TokenRange=29:39";

        String text3 = "# generator = UDPipe 2, https://lindat.mff.cuni.cz/services/udpipe\n" + 
                "# udpipe_model = italian-isdt-ud-2.12-230717\n" +
                "# udpipe_model_licence = CC BY-NC-SA\n" +
                "# newdoc\n" +
                "# newpar\n" +
                "# sent_id = 1\n" +
                "# text = il tipo è produzione\n" +
                "1\til\til\tDET\tRD\tDefinite=Def|Gender=Masc|Number=Sing|PronType=Art\t2\tdet\t_\tTokenRange=0:2\n" +
                "2\ttipo\ttipo\tNOUN\tS\tGender=Masc|Number=Sing\t4\tnsubj\t_\tTokenRange=3:7\n" +
                "3\tè\tessere\tAUX\tVA\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin\t4\tcop\t_\tTokenRange=8:9\n" +
                "4\tproduzione\tproduzione\tNOUN\tS\tGender=Fem|Number=Sing\t0\troot\t_\tSpaceAfter=No|TokenRange=10:20";
*/

        List<Word> words = parseText(text);

        DependencyTree tree = buildTree(words);
        if (tree != null) {
            tree.printTree("");
        }else {
            System.out.println("NULLO");
        }

       Lexicon italianLexicon = new ITXMLLexicon();
       NLGFactory factory = new NLGFactory(italianLexicon);
       Realiser realiser = new Realiser();

       String output = null;

       boolean isPassive = tree.isPassive();
       DependencyTree subj = tree.findSubject();
       DependencyTree verb = tree.findVerb();
       DependencyTree obj = tree.findObject();

       // System.out.println("Subject: " + subj.root.lemma);
       // System.out.println("Verb: " + verb.root.lemma);
       // System.out.println("Object: " + obj.root.lemma);

       NPPhraseSpec np_subj, np_obj;
       VPPhraseSpec vp = factory.createVerbPhrase(verb.root.lemma);

       vp.setFeature(Feature.FORM, Form.NORMAL);
        // System.out.println("passive" + isPassive);
       if (!isPassive) {
           vp.setFeature(Feature.PERFECT, verb.isPerfect());
       }
       vp.setFeature(Feature.TENSE, Tense.PRESENT);


       if (subj.findDeterminer() != null) {
           // System.out.println("Determiner: " + subj.findDeterminer().root.lemma);
           // System.out.println("Lemma: " + subj.root.lemma);
           np_subj = factory.createNounPhrase(subj.findDeterminer().root.form, subj.root.lemma);
       }else {
           np_subj = factory.createNounPhrase(subj.root.lemma);
       }

       if(subj.root.feats.containsKey("Gender")){
           // System.out.println("sogg " + subj.root.feats.get("Gender") + " " + subj.root.feats.get("Gender").equals("Fem"));
           np_subj.setFeature(LexicalFeature.GENDER,Gender.FEMININE);
       }

       if (obj.findDeterminer() != null) {
           np_obj = factory.createNounPhrase(obj.findDeterminer().root.form, obj.root.lemma);
       }else {
           np_obj = factory.createNounPhrase(obj.root.lemma);
       }

       if(obj.root.feats.containsKey("Gender")){
           //System.out.println(obj.root.feats.get("Gender").equals("Fem"));
           np_obj.setFeature(LexicalFeature.GENDER, obj.root.feats.get("Gender").equals("Fem") ?  Gender.FEMININE : Gender.MASCULINE);
       }

       SPhraseSpec proposition = factory.createClause(np_subj, vp, np_obj);

       if (intType.equals("WHAT_SUBJECT")){
              proposition.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.WHO_SUBJECT);
       }else{
           proposition.setFeature(Feature.INTERROGATIVE_TYPE, InterrogativeType.valueOf(intType));
       }

       if (isPassive) {
           proposition.setFeature(Feature.PASSIVE, true);
       }


       output = realiser.realiseSentence(proposition);
       if (intType.equals("WHAT_SUBJECT")){
           output = output.replace("Chi", "Cosa");
       }
       System.out.println(output);

    }
}

class Word {
    int id;
    String form;
    String lemma;
    String upos;
    String xpos;
    Map<String, String> feats;
    int head;
    String deprel;
    String deps;
    String misc;

    public Word(int id, String form, String lemma, String upos, String xpos, String feats, int head, String deprel, String deps, String misc) {
        this.id = id;
        this.form = form;
        this.lemma = lemma;
        this.upos = upos;
        this.xpos = xpos;
        this.feats = parseFeats(feats);
        this.head = head;
        this.deprel = deprel;
        this.deps = deps;
        this.misc = misc;
    }



    public static Map<String, String> parseFeats(String feats) {
        Map<String, String> featsMap = new HashMap<>();

        if (feats == null || feats.trim().isEmpty()) {
            return featsMap; // Return an empty map if no features are present
        }

        String[] pairs = feats.split("\\|");

        for (String pair : pairs) {
            String[] keyValue = pair.split("=");
            if (keyValue.length == 2) {
                featsMap.put(keyValue[0], keyValue[1]);
            } else {
                // Handle cases where there might be an incorrect format
                featsMap.put(keyValue[0], "");
            }
        }

        return featsMap;
    }

    @Override
    public String toString() {
        return id + "\t" + form + "\t" + lemma + "\t" + upos + "\t" + xpos + "\t" + feats + "\t" + head + "\t" + deprel + "\t" + deps + "\t" + misc;
    }
}

class DependencyTree {
    Word root;
    List<DependencyTree> children;

    public DependencyTree(Word root) {
        this.root = root;
        this.children = new ArrayList<>();
    }

    public DependencyTree findSubject() {
        for (DependencyTree child : children) {
            if (child.root.deprel.equals("nsubj") || child.root.deprel.equals("nsubj:pass")) {
                return child;
            }
        }
        return null;
    }

    public DependencyTree findObject() {
        for (DependencyTree child : children) {
            if (child.root.deprel.equals("obj" ) || child.root.deprel.equals("obl:agent") || (!child.root.deprel.equals("nsubj") &&  !child.root.upos.equals("NOUN"))) {
                return child;
            }
        }
        return null;
    }

    public DependencyTree findVerb() {
        //has upos equal VERB
        if (root.upos.equals("VERB")) {
            return this;
        }
        for (DependencyTree child : children) {
            DependencyTree verb = child.findVerb();
            if (verb != null) {
                return verb;
            }
        }
        if (root.xpos.equals("VA")) {
            return this;
        }
        for (DependencyTree child : children) {
            DependencyTree verb = child.findVerb();
            if (verb != null) {
                return verb;
            }
        }
        return null;
    }

    //find my determiner in my direct childrens (upos equal DET)
    public DependencyTree findDeterminer() {
        for (DependencyTree child : children) {
            if (child.root.upos.equals("DET")) {
                return child;
            }
        }
        return null;
    }

    //function get verb tense
    public boolean isPerfect(){
        if(root.feats.containsKey("Tense")){
            String myTense = root.feats.get("Tense");
            //check if direct children is upos aux and has tense
            for (DependencyTree child : children) {

                if (child.root.upos.equals("AUX") && child.root.feats.containsKey("Tense")) {
                    String childTense = child.root.feats.get("Tense");
                    //if child tense is Pres and mine is Past returntrue
                    if(childTense.equals("Pres") && myTense.equals("Past")){
                        return true;
                    }
                }
            }
            return false;
        }
        return false;
    }

    public void addChild(DependencyTree child) {
        this.children.add(child);
    }

    public void printTree(String prefix) {
        // System.out.println(prefix + root);
        for (DependencyTree child : children) {
            child.printTree(prefix + "  ");
        }
    }

    public boolean isPassive() {
        for (DependencyTree child : children) {
            if (child.root.deprel.equals("aux:pass") && child.root.lemma.equals("essere")) {
                return true;
            }
        }
        return false;
    }
}


