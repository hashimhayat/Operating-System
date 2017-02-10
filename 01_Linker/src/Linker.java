/**
 * Created by Hashim Hayat on 1/27/17.
 */

public class Linker extends InstructionParser {

    public Linker(String filePath) {
        super(filePath);
    }

    public static void main(String[] args){

        String filePath = args[0];

        InstructionParser parser = new InstructionParser(filePath);

        parser.performFirstPass();
        parser.performSecondPass();


        parser.printMemoryMap();
        parser.printSymbolTable();
        //parser.printModuleAddr();

        System.out.println(parser.ErrorsMessageGenerator());

    }
}
