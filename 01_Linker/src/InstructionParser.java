
/*
 * Operating Systems - Lab 1 - Two Pass Linker
 * Created by Hashim Hayat on 1/27/17.
 */

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.*;

public class InstructionParser {

    // MAX MACHINE SIZE
    public static final int MACHINE_SIZE = 200;
    // Contains the input data in a string format
    private String[] dataBuffer;
    // Contains all error messages
    private String error_messages = "\n::Errors & Warning::\n";
    // Contains total number of modules
    int modules = 0;

    // A list of instruction types [A, I, E, R]
    ArrayList<String> adrList = new ArrayList<String>(4);
    // Holds the relative address of each module
    private HashMap<Integer, Integer> moduleAddr = new HashMap<Integer, Integer>();
    // Holds the symbols and their relative address after first pass
    HashMap<String, Integer> symbolTable = new HashMap<String, Integer>();
    // Keep tracks of symbolUsage - Error Handling purposes
    private TreeMap<String, Integer> symbolUsage = new TreeMap<String, Integer>();
    // Contains the final Memory Map
    ArrayList memoryMap = new ArrayList();

    // Custom custructor to reads the input file and fill
    // Store the input data into the dataBuffer.
    InstructionParser(String filePath){
        readFile(filePath);
        modules = Integer.parseInt(dataBuffer[0]);
        adrList.add("A"); adrList.add("I"); adrList.add("E"); adrList.add("R");
    }

    // Function that reads the file and fills in the dataBuffer
    private void readFile(String filePath){

        String fileContent = "";

        try (BufferedReader buffer = new BufferedReader(new FileReader(filePath))) {

            String currentLine;

            while ((currentLine = buffer.readLine()) != null) {
                fileContent += currentLine;
                fileContent += '\n';
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
        dataBuffer = fileContent.replaceAll("\\s+", " ").trim().split(" ");
    }

    // Debugger function to print data in the buffer of type String[]
    public static void printData(String[] buff) {
        for (int i = 0; i < buff.length; ++i){
            System.out.print(buff[i] + " ");
        }
    }

    // Prints the key -> Value pairs of a hashmap
    public static void printMap(HashMap mp) {
        System.out.println("\n::Symbol Table::");
        Iterator it = mp.entrySet().iterator();
        while (it.hasNext()) {
            HashMap.Entry pair = (HashMap.Entry)it.next();
            System.out.println(pair.getKey() + " = " + pair.getValue());
        }
    }

    public void printMemoryMap(){

        int offset = 0;
        System.out.println("::Memory Map::");
        for (Object m : memoryMap) {
            System.out.print(offset);
            System.out.println(":   " + m);
            offset++;
        }
    }

    // Checks if we have a non-empty use list
    public boolean isUseList(int idx){

        while (idx < dataBuffer.length){

            if (Character.isLetter(dataBuffer[idx].charAt(0)))
                return false;
            if (Integer.parseInt(dataBuffer[idx]) == -1)
                return true;

            idx++;
        }
        return false;
    }

    // Performs the external referencing
    public String performExternalRef(int adr, int ins){

        String addr = String.valueOf(adr);
        String inst = String.valueOf(ins);

        if (adr == 0){
            addr = "000";
        }

        int l = 0;
        int len = inst.length() - addr.length();
        StringBuilder output = new StringBuilder(inst.length());

        for (int i = 0; i < len; i++)
            output.append(inst.charAt(i));

        while (l < addr.length()){
            output.append(addr.charAt(l));
            l++;
        }

        return output.toString();
    }

    public boolean isGreaterThanMachineSize(int adr){

        String addr = String.valueOf(adr).substring(1);

        if (Integer.parseInt(addr) > MACHINE_SIZE-1)
            return true;
        return false;
    }

    public boolean isGreaterThanModuleSize(int module_size, int addr){

        String adr = String.valueOf(addr).substring(1);

        if (Integer.parseInt(adr) > module_size-1)
            return true;
        return false;
    }

    // Use zero
    public String useZero(int ins){

        String addr = "000";
        String inst = String.valueOf(ins);

        int l = 0;
        int len = inst.length() - addr.length();
        StringBuilder output = new StringBuilder(inst.length());

        for (int i = 0; i < len; i++)
            output.append(inst.charAt(i));

        while (l < addr.length()){
            output.append(addr.charAt(l));
            l++;
        }

        return output.toString();
    }

    /*
        Performs the First Pass.
        Creates the symbol table and module addr table.
    */
    public int performFirstPass(){

        moduleAddr.put(1,0);
        boolean firstPassed = false;
        int module_insight = 2; // module_insight - 1 is the module we are in
        int i = 1;

        while (!firstPassed){

            if (dataBuffer[i].equals("R") || dataBuffer[i].equals("E") || dataBuffer[i].equals("A") || dataBuffer[i].equals("I")){

                if (modules >= moduleAddr.size()) {

                    moduleAddr.put(module_insight, moduleAddr.get(module_insight - 1) + Integer.parseInt(dataBuffer[i - 1]));
                    int offset = Integer.parseInt(dataBuffer[i - 1]) * 2;

                    if (i + offset < dataBuffer.length) {
                        i += offset;
                        module_insight++;
                    }
                }
            } else if(Character.isLetter(dataBuffer[i].charAt(0)) && !isUseList(i + 1)){

                // Putting symbol and its relative address in the symbol table
                int relativeAddr = Integer.parseInt(dataBuffer[i + 1]) + moduleAddr.get(module_insight - 1);

                // moduleAddr.get(module_insight - 1); is the max addr of the module]

                if (relativeAddr <= moduleAddr.get(module_insight - 1)){
                    if (!symbolTable.containsKey(dataBuffer[i]))
                        symbolTable.put(dataBuffer[i],relativeAddr);
                    else
                        error_messages += "Error: Variable " + dataBuffer[i] + " is multiply defined; first value used.\n";
                } else {
                    error_messages += "Error: Definition of " + dataBuffer[i] + " exceeds module size; first word in module used.\n";
                    symbolTable.put(dataBuffer[i],0 + moduleAddr.get(module_insight - 1));
                }

                // Updating symbol usage table
                symbolUsage.put(dataBuffer[i],module_insight - 1);
            }

            i++;

            if (i == dataBuffer.length){
                firstPassed = true;
                return 0;
            }
        }
        return -1;
    }

    /*
        Performs the second pass.
    */

    public int performSecondPass(){

        boolean secondPassed = false;
        boolean foundUselist = false;
        int count = 0;
        int module = 1;
        int i = 1;

        HashMap<Integer, String> variableUsage = new HashMap<Integer, String>();


        while (!secondPassed){

            foundUselist = false;
            count = 0;

            // Looks for a non empty use list.
            if (Character.isLetter(dataBuffer[i].charAt(0)) && isUseList(i + 1) ){

                foundUselist = true;

                // number of use-able variables
                count = Integer.parseInt(dataBuffer[i - 1]);

                int var_seen = 0;
                int j = 0;

                variableUsage.clear();

                while (foundUselist){

                    // i is the idx of the variable
                    // j is the idx of the first idx

                    j = i + 1;
                    String var = dataBuffer[j - 1];
                    var_seen++;

                    while(Integer.parseInt(dataBuffer[j]) != -1){

                        if (!variableUsage.containsKey(Integer.parseInt(dataBuffer[j])))
                            variableUsage.put(Integer.parseInt(dataBuffer[j]), var);
                        else
                            error_messages += "Error: Multiple variables used in instruction; all but first ignored.\n";
                            symbolUsage.put(var,-1);
                        j++;
                    }

                    // first variable has been added j is at -1
                    // bring j to first index
                    i = j + 1;

                    // read one use list module
                    if (var_seen == count){

                        // creating the memory map here

                        // i -> the number of program text instructions
                        int ptext_N = Integer.parseInt(dataBuffer[i]);

                        // idx of instruction
                        int ins_idx = i + 1;

                        // first instruction
                        String ins = dataBuffer[ins_idx];

                        // idx of the instruction
                        int ins_count = 0;

                        /*
                         * (1) an Immediate operand, which is unchanged;
                         * (2) an Absolute address, which is unchanged;
                         * (3) a Relative address, which is relocated; add module addr
                         * (4) an External address, which is resolved. change last digits to that of the variable
                        */

                        int addr;

                        while (ins_count < ptext_N){

                            addr = Integer.parseInt(dataBuffer[ins_idx + 1]);

                            if (dataBuffer[ins_idx].equals("I")){

                                memoryMap.add(addr);

                            } else if (dataBuffer[ins_idx].equals("A")){

                                if (isGreaterThanMachineSize(addr)){
                                    error_messages += "Error: Absolute address " + addr + " exceeds machine size; zero used.\n";
                                    memoryMap.add(useZero(addr));
                                }
                                else
                                    memoryMap.add(addr);

                            }
                            else if (dataBuffer[ins_idx].equals("R")){

                                int module_size = ptext_N;

                                if (isGreaterThanModuleSize(module_size, addr)) {
                                    error_messages += "Error: Relative address " + addr + " exceeds module size; zero used.\n";

                                    memoryMap.add(useZero(addr));
                                } else {
                                    memoryMap.add(addr + moduleAddr.get(module));
                                }
                            }
                            else if (dataBuffer[ins_idx].equals("E")) {

                                if (symbolTable.containsKey(variableUsage.get(ins_count))){

                                    memoryMap.add(performExternalRef(symbolTable.get(variableUsage.get(ins_count)), addr));

                                    // Update symbol usage.
                                    symbolUsage.put(variableUsage.get(ins_count),-1);
                                } else {
                                    memoryMap.add(useZero(addr));

                                    error_messages += "Error: " + variableUsage.get(ins_count) + " is not defined; zero used.\n";
                                }
                            }

                            ins_idx += 2;
                            ins_count++;
                            i += 2;
                        }

                        module++;
                        foundUselist = false;
                    }
                }
            }

            //Found an empty use list
            else if (!Character.isLetter(dataBuffer[i].charAt(0)) && Integer.parseInt(dataBuffer[i]) == 0 && adrList.contains(dataBuffer[i+2])){

                    // i + 1 = number of instructions
                    // i + 2 is the instruction type
                    // i + 3 is the first instruction

                    int ptext_N = Integer.parseInt(dataBuffer[i + 1]);
                    String inst_type = dataBuffer[i + 2];
                    int ins_count = 0;

                    while (ins_count < ptext_N){

                        int inst = Integer.parseInt(dataBuffer[i + 3]);

                        if (inst_type.equals("A")){

                            if (isGreaterThanMachineSize(inst)){
                                error_messages += "Error: Absolute address " + inst + " exceeds machine size; zero used.\n";
                                memoryMap.add(useZero(inst));
                            }
                            else
                                memoryMap.add(inst);
                        }

                        else if (inst_type.equals("I")){

                            memoryMap.add(inst);

                        }
                        else if (inst_type.equals("R")){

                            int module_size = ptext_N;

                            if (isGreaterThanModuleSize(module_size, inst)) {
                                error_messages += "Error: Relative address " + inst + " exceeds module size; zero used.\n";

                                memoryMap.add(useZero(inst));
                            } else {
                                memoryMap.add(inst + moduleAddr.get(module));
                            }
                        }

                        i += 2;
                        ins_count++;
                    }
            }

            i++;

            if (i == dataBuffer.length){
                secondPassed = true;
                return 0;
            }
        }
        return -1;
    }

    // Generates error messages.
    public String ErrorsMessageGenerator(){

        String errors = "";

        Iterator it = symbolUsage.entrySet().iterator();
        while (it.hasNext()) {
            HashMap.Entry pair = (HashMap.Entry)it.next();
            if (!pair.getValue().equals(-1)) {
                errors += "Warning: " + pair.getKey() + " was defined in module " + pair.getValue() + " but never used.\n";
            }
            it.remove();
        }

        error_messages += errors;
        return error_messages;
    }

}