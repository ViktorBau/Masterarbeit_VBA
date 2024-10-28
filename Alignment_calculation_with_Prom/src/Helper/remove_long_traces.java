package Helper;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeSet;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.deckfour.xes.model.impl.XLogImpl;

import Helper.logToLogOfTraceVariants;
import Prom_without_Prom.Prom_without_Prom_Helper;




public class remove_long_traces {
	public static  ArrayList sorted_trace_length(XLog log){
	ArrayList taceLength = new ArrayList();
	for (XTrace trace: log){
		taceLength.add(trace.size());
	};
	Collections.sort(taceLength);
	int index = (int) Math.ceil(0.95 * taceLength.size()) - 1;
	int percentileValue = (int) taceLength.get(index);
	
	return taceLength;
	
	}
	public static ArrayList sorted_trace_variant_length(XLog log) {
		
		XLog log_variants = (XLog) logToLogOfTraceVariants.LogToLogOfVariants(log).get(0);
		
		ArrayList taceLength = new ArrayList();
		
		for (XTrace trace: log_variants){
			taceLength.add(trace.size());
		};
		
		
		
		return taceLength;
	}
	
	public static XLog deleteTracesLongerX(XLog log, Integer length) {
		
		 XLog filteredLog = new XLogImpl(log.getAttributes());
		 for (int i = 0; i < log.size(); i++) {
	            XTrace trace = log.get(i);
	           if (trace.size() <length+1) {
	        	   filteredLog.add(trace);
	           }
		};
		return filteredLog;
		
	}
	public static XLog deleteTracesShorterX(XLog log, Integer length) {
		
		 XLog filteredLog = new XLogImpl(log.getAttributes());
		 for (int i = 0; i < log.size(); i++) {
	            XTrace trace = log.get(i);
	           if (trace.size() >length+1) {
	        	   filteredLog.add(trace);
	           }
		};
		return filteredLog;
		
	}
	

	public static void printLengthCounts(ArrayList<Integer> traceLength, ArrayList<Integer> traceVariantLength) {
	    Map<Integer, Integer> traceLengthCounts = countLengths(traceLength);
	    Map<Integer, Integer> traceVariantLengthCounts = countLengths(traceVariantLength);
	    
	    int totalTraceCount = traceLength.size();
	    int totalTraceVariantCount = traceVariantLength.size();

	    System.out.println("Length\tTrace Count\tTrace Variant Count\tCumulative Trace %\tCumulative Trace Variant %");
	    System.out.println("------\t-----------\t------------------\t-----------------\t-----------------------");

	    // Get all unique lengths from both lists
	    TreeSet<Integer> allLengths = new TreeSet<>(traceLengthCounts.keySet());
	    allLengths.addAll(traceVariantLengthCounts.keySet());

	    int cumulativeTraceCount = 0;
	    int cumulativeTraceVariantCount = 0;

	    for (Integer length : allLengths) {
	        int traceCount = traceLengthCounts.getOrDefault(length, 0);
	        int traceVariantCount = traceVariantLengthCounts.getOrDefault(length, 0);

	        cumulativeTraceCount += traceCount;
	        cumulativeTraceVariantCount += traceVariantCount;

	        double cumulativeTracePercentage = (double) cumulativeTraceCount / totalTraceCount * 100;
	        double cumulativeTraceVariantPercentage = (double) cumulativeTraceVariantCount / totalTraceVariantCount * 100;

	        System.out.printf("%d\t%d\t\t%d\t\t\t%.2f%%\t\t\t\t%.2f%%%n",
	                length, traceCount, traceVariantCount, cumulativeTracePercentage, cumulativeTraceVariantPercentage);
	    }
	}

	public static Map<Integer, Integer> countLengths(ArrayList<Integer> lengths) {
	    Map<Integer, Integer> lengthCounts = new HashMap<>();
	    for (Integer length : lengths) {
	        lengthCounts.put(length, lengthCounts.getOrDefault(length, 0) + 1);
	    }
	    return lengthCounts;
	}


	  public static void writeLengthCountsToFile(ArrayList<Integer> traceLength, ArrayList<Integer> traceVariantLength, int cutOff, String fileName) {
	        Map<Integer, Integer> traceLengthCounts = countLengths(traceLength);
	        Map<Integer, Integer> traceVariantLengthCounts = countLengths(traceVariantLength);
	        
	        int totalTraceCount = traceLength.size();
	        int totalTraceVariantCount = traceVariantLength.size();

	        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
	            writer.write("Chosen cut-off: " + cutOff + "\n");
	            writer.write("Length\tTrace Count\tTrace Variant Count\tCumulative Trace %\tCumulative Trace Variant %\n");
	            writer.write("------\t-----------\t------------------\t-----------------\t-----------------------\n");

	            // Get all unique lengths from both lists
	            TreeSet<Integer> allLengths = new TreeSet<>(traceLengthCounts.keySet());
	            allLengths.addAll(traceVariantLengthCounts.keySet());

	            int cumulativeTraceCount = 0;
	            int cumulativeTraceVariantCount = 0;

	            for (Integer length : allLengths) {
	                int traceCount = traceLengthCounts.getOrDefault(length, 0);
	                int traceVariantCount = traceVariantLengthCounts.getOrDefault(length, 0);

	                cumulativeTraceCount += traceCount;
	                cumulativeTraceVariantCount += traceVariantCount;

	                double cumulativeTracePercentage = (double) cumulativeTraceCount / totalTraceCount * 100;
	                double cumulativeTraceVariantPercentage = (double) cumulativeTraceVariantCount / totalTraceVariantCount * 100;

	                writer.write(String.format("%d\t%d\t\t%d\t\t\t%.2f%%\t\t\t\t%.2f%%%n",
	                        length, traceCount, traceVariantCount, cumulativeTracePercentage, cumulativeTraceVariantPercentage));
	            }
	        } catch (IOException e) {
	            e.printStackTrace();
	        }
	    }
	
	public static void main(String[] args) throws Exception {
		
		//Path pathToEventlog = Paths.get("/vol","fob-vol3","mi20","baumanem","alignments","BPI_2012_remove_longest_traces");
		Path pathToEventlog = Paths.get("C:","Users","bauma","Desktop","Masterarbeit","Alignments","Road_traffic_delted_long_traces");
			
				String nameOfEventLog = "Event_Log.xes";
				
				
				XLog log = Prom_without_Prom_Helper.readSingleLog(pathToEventlog.resolve(nameOfEventLog).toFile());
				
				ArrayList traceVariantLengths = sorted_trace_variant_length(log);
				ArrayList traceLengths = sorted_trace_length(log);
				
				printLengthCounts(traceLengths,traceVariantLengths );
				
				Integer cutOff = 9;
				
				XLog logFiltered = deleteTracesLongerX(log, cutOff);
				writeLengthCountsToFile(traceLengths,traceVariantLengths, cutOff, pathToEventlog.resolve("trace_length_cut_off").toString());
				Prom_without_Prom_Helper.exportSingleLog(logFiltered, pathToEventlog.resolve("Event_log_filtered.xes").toString());
				

		
	}
}
