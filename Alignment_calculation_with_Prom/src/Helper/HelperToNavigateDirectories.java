package Helper;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;

import org.deckfour.xes.model.XLog;

public class HelperToNavigateDirectories {
	
	 public static void main(String[] args) {
	
	Path pathToEventlog = Paths.get("C:","Users","bauma","Desktop","Masterarbeit","Alignments","Road_Traffic_Fine_Management_Process");
	

   
	ArrayList test = getAllModelsFromDir(pathToEventlog);
	String as ="asd";
	 }
   
	
	   public static ArrayList<String> getAllModelsFromDir(Path directoryPath) {
	        ArrayList<String> modelDirectories = new ArrayList<>();
	        
	        // Create a File object representing the directory
	        File directory =  directoryPath.toFile();
	        
	        // Check if the given path is a directory
	        if (directory.isDirectory()) {
	            // Get list of all files and directories in the specified directory
	            File[] files = directory.listFiles();
	            
	            // Iterate over each file/directory
	            for (File file : files) {
	                // Check if it's a directory and starts with "model_"
	                if (file.isDirectory() && file.getName().startsWith("Model_")) {
	                    // Add the name of the subdirectory to the list
	                    modelDirectories.add(file.getName().toString());
	                }
	            }
	        } else {
	            System.out.println("Provided path is not a directory.");
	        }
	        
	        return modelDirectories;
	    }
	   
	

}
