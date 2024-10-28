package cleanLog;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;

import org.deckfour.xes.model.*;
import org.deckfour.xes.model.impl.*;
import org.deckfour.xes.factory.*;
import org.deckfour.xes.id.XID;
import org.deckfour.xes.extension.std.*;
import org.deckfour.xes.in.XesXmlParser;
import org.deckfour.xes.out.XesXmlSerializer;

import Helper.remove_long_traces;
import Prom_without_Prom.Prom_without_Prom_Helper;
import java.util.Scanner;

public class cleanLog {
	public static XLog filterIncomplete(XLog log) {
        XLog filteredLog = new XLogImpl(log.getAttributes());

        
        for (XTrace trace : log) {
            XTrace newTrace = (XTrace) trace.clone();
        
           
            for (XEvent event : trace) {
                if (!event.getAttributes().get("lifecycle:transition").toString().equalsIgnoreCase("complete" )) {
                	int indexNewTrace = 0;
                	for (XEvent newEvent : newTrace) {
                			if (newEvent.getAttributes().toString().equals(event.getAttributes().toString())){
                				newTrace.remove(indexNewTrace);
                				break;
                				
                			}
                			indexNewTrace++;
                	}
                }
            }
            
            // Add the trace to the new log if it has any complete events
            if (!newTrace.isEmpty()) {
                filteredLog.add(newTrace);
            }
            else {
            	System.out.print("Careful!! a full trace deleted because it did not contain a single completed Event");
            }
        }
        return filteredLog;
    }


public static void main(String[] args) throws Exception {
	 
		//Path pathToEventlog = Paths.get("/vol","fob-vol3","mi20","baumanem","alignments","BPI_2012_remove_longest_traces");
		Path pathToEventlog = Paths.get("C:","Users","bauma","Desktop","Masterarbeit","Alignments","BPI_2012_new_mapping");
			
				String nameOfEventLog = "Event_Log.xes";
				
				
				XLog log = Prom_without_Prom_Helper.readSingleLog(pathToEventlog.resolve(nameOfEventLog).toFile());
				
				XLog logOnlyComplete = filterIncomplete(log);
				ArrayList traceVariantLengths = remove_long_traces.sorted_trace_variant_length(logOnlyComplete);
				ArrayList traceLengths = remove_long_traces.sorted_trace_length(logOnlyComplete);
				
				remove_long_traces.printLengthCounts(traceLengths,traceVariantLengths );
				
				Scanner scanner = new Scanner(System.in);
		        
		        System.out.println("Please enter the disred cutoff:");

		        // Waits for the user to input an integer
		        int cutOff = scanner.nextInt();
		        
		        scanner.close();
				XLog logFiltered = remove_long_traces.deleteTracesLongerX(logOnlyComplete, cutOff);
				remove_long_traces.writeLengthCountsToFile(traceLengths,traceVariantLengths, cutOff, pathToEventlog.resolve("trace_length_cut_off_"+cutOff+".txt").toString());
				Prom_without_Prom_Helper.exportSingleLog(logFiltered, pathToEventlog.resolve("Event_log_filtered_cut_off_"+cutOff+".xes").toString());
				

		
	}
}
