/**
 * Created by Hashim Hayat on 1/27/17.
 */


/*
* - go char by char ignoring spaces and 0

- Store the opcode n then identify what sort of n object is has

Identifying the object:

- definition list
    its a pair of (sym, loc) which is string, integer

- use list
    variable integers terminated by -1

- program text
    have either R/E/A/I and a four number instruction

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
        printMap(parser.symbolTable);

        System.out.println(parser.ErrorsMessageGenerator());

    }
}
