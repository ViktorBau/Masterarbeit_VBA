package alignment_calculation;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Collections;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Hashtable;
import java.util.List;

import org.deckfour.xes.classification.XEventClass;
import org.deckfour.xes.classification.XEventClassifier;
import org.deckfour.xes.info.impl.XLogInfoImpl;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.deckfour.xes.model.impl.XLogImpl;
import org.processmining.framework.plugin.PluginContext;
import org.processmining.log.utils.TraceVariant;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.graphbased.directed.petrinet.PetrinetGraph;
import org.processmining.models.graphbased.directed.petrinet.elements.Place;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;
import org.processmining.plugins.petrinet.replayer.matchinstances.algorithms.express.AllOptAlignmentsGraphAlg;
import org.processmining.plugins.petrinet.replayer.matchinstances.algorithms.express.AllOptAlignmentsGraphAlgDebug;
import org.processmining.plugins.petrinet.replayer.matchinstances.algorithms.express.ParamSettingExpressAlg;
import org.processmining.plugins.petrinet.replayresult.PNMatchInstancesRepResult;
import org.processmining.plugins.petrinet.replayresult.StepTypes;
import org.processmining.plugins.pnml.base.Pnml.PnmlType;
import org.processmining.plugins.replayer.replayresult.AllSyncReplayResult;

import com.fasterxml.jackson.databind.ObjectMapper;

import Helper.HelperToNavigateDirectories;
import Helper.remove_long_traces;
import Helper.sort_event_log_by_trace_length;
import Prom_without_Prom.Prom_without_Prom_Helper;
import Helper.delete_traces_by_name;
import Helper.logToLogOfTraceVariants;
import Helper.removeTraceVariantsByName;
import Helper.createEventLogSingleTraces;



public class All_optimal_alignments {
	public static void main(String[] args) throws Exception {
		
		 ObjectMapper objectMapper = new ObjectMapper();
				// Path to Eventlog and model folder name needs to be added as because this class is written to be called programmatically through the all_optimal_worker
		String dirModel = args[0];
		String pathToEventLogString = args[1];
		Path pathToEventLog = Paths.get(pathToEventLogString);
		Path pathToModel = pathToEventLog.resolve(dirModel);
		
		Path pathToResult = pathToModel.resolve("PROM_alignment_results");
		 if (!Files.exists(pathToResult)) {
			 Files.createDirectories(pathToResult);
		 }
		List tracesFinished = new ArrayList<>();
		try {
		tracesFinished = readCSV(pathToResult.resolve("traces_finished.csv").toString());}
		catch (Exception e) {	}
		
		List<String> tracesToExclude = new ArrayList<>();
		try {
			tracesToExclude = readCSV(pathToModel.resolve("traces_excluded.csv").toString());}
		catch (Exception e) {	}
		

		
		String nameOfEventLog = "Event_Log.xes";
		String fileNameAlignment = "PROM_all_optimal.json";
		String Filename_mapping = "all_optimal_alignments_mapping_variant_traces.json";
		
	
		
		XLog logOrginal = Prom_without_Prom_Helper.readSingleLog(pathToEventLog.resolve(nameOfEventLog).toFile());
		
		ArrayList variantLogMapping = logToLogOfTraceVariants.LogToLogOfVariants(logOrginal);
		
		
		//delete the variants from log that led to OOM events and save the mapping 
		XLog variantLog = (XLog) variantLogMapping.get(0);
		
		Object[] petri= Prom_without_Prom_Helper.importFromFile(pathToModel.resolve("Petri_net.pnml").toFile(), "Petri_net");
		PetrinetGraph net = (PetrinetGraph) petri[0];

		
		XEventClass dummyEvClass = new XEventClass("DUMMY", 99999);
		XEventClassifier eventClassifier = XLogInfoImpl.STANDARD_CLASSIFIER;
		
		TransEvClassMapping mapping = Prom_without_Prom_Helper.constructMapping(net, variantLog, dummyEvClass,
				eventClassifier, false);
	
		ParamSettingExpressAlg parameters =  new ParamSettingExpressAlg();
		
		parameters.populateCostPanel(net, variantLog, mapping);
		
		
		Object[] parametersAll = parameters.getAllParameters();
		
		Object[] parametersObject = new Object[4];
		parametersObject[0] = parametersAll[0];
		parametersObject[1] = Integer.MAX_VALUE;
		parametersObject[2] = parametersAll[2];
		parametersObject[3] = pathToModel;
		
		
		XLog log_excluded = delete_traces_by_name.delete_traces_by_name(variantLog, tracesToExclude);	
		
		//delete trace variants already processed
		XLog logTracesLeft = delete_traces_by_name.delete_traces_by_name(log_excluded, tracesFinished);
		
		
		System.out.println("Starting on" + dirModel);
		 //save mapping
		
		
		
		
		for (XTrace trace : logTracesLeft) {
			XLog log = createEventLogSingleTraces.createEventLogSingleTraces(logTracesLeft, trace);
		
		
		
		PluginContext context = null; 
		
		
	
		
		AllOptAlignmentsGraphAlgDebug alignmentAlg = new AllOptAlignmentsGraphAlgDebug();
		
		PNMatchInstancesRepResult allOptimal = alignmentAlg.replayLog(context, net, Prom_without_Prom_Helper.getInitialMarking(net), Prom_without_Prom_Helper.getFinalMarking(net),log,mapping,parametersObject);
		
		System.out.println("Got results, starting conversion");
		
		Hashtable<String, Hashtable<String, Object>> alignmentResults = new Hashtable<>();
		
		for (AllSyncReplayResult traceVariant: allOptimal){
			Hashtable<String, Object> variantResult = new Hashtable<>();
			variantResult.put("info",traceVariant.getInfo() );
			
			// changing the single Events from Transition Objects to String to make serialization with objectmapper easier
			ArrayList nodeInstanceList = new ArrayList();
			for (List<Object> alignment:traceVariant.getNodeInstanceLst()){
				ArrayList alignmentList = new ArrayList();
				for (Object event:alignment){
					alignmentList.add(event.toString());
				}
				nodeInstanceList.add(alignmentList);
				
			}
			
			// same for steptypes
			
			ArrayList stepTypesList = new ArrayList();
			for (List<StepTypes> alignment:traceVariant.getStepTypesLst()){
				ArrayList alignmentList = new ArrayList();
				for (Object stepType:alignment){
					alignmentList.add(stepType.toString());
				}
				stepTypesList.add(alignmentList);
				
			}
		
			variantResult.put("nodeInstance",nodeInstanceList);
			variantResult.put("stepTypes", stepTypesList);
			variantResult.put("traceIndicies",traceVariant.getTraceIndex() );
			String traceName = log.get(traceVariant.getTraceIndex().first()).getAttributes().get("concept:name").toString();
			alignmentResults.put(traceName, variantResult);
			
			 try (BufferedWriter writer = new BufferedWriter(new FileWriter(pathToResult.resolve("traces_finished.csv").toString(), true))) {
				  writer.write(traceName);
		          writer.newLine();
	      } catch (IOException e) {
	          e.printStackTrace();
	      }
		}
		
		System.out.println("finished conversion,saving results");
		
		  if (pathToResult.resolve(fileNameAlignment).toFile().exists()) {
			  Hashtable<String, Hashtable<String, Object>> finishedAlignments = objectMapper.readValue(pathToResult.resolve(fileNameAlignment).toFile(), Hashtable.class);
			  for (String key : alignmentResults.keySet()) {
		            Hashtable<String, Object> value = alignmentResults.get(key);
		            finishedAlignments.put(key,value);
		        }
			
			  objectMapper.writeValue(pathToResult.resolve(fileNameAlignment).toFile(), finishedAlignments);
              
              
              
          } else {
        	  
        	  objectMapper.writeValue(pathToResult.resolve(fileNameAlignment).toFile(), alignmentResults);
          }
		 
		}
		// Create Eventlog where the trace variants which cause OOM Problems are excluded 
		// And the mapping from trace Variants to single traces 
	
	
		logOrginal = Prom_without_Prom_Helper.readSingleLog(pathToEventLog.resolve(nameOfEventLog).toFile());
		
		//Log without problematic traces
	    XLog  logExcluded = removeTraceVariantsByName.removeTraceVariantsByName(logOrginal, tracesToExclude);
	    
	    
	    ArrayList variantLogMappingExcluded = logToLogOfTraceVariants.LogToLogOfVariants(logExcluded);
	
			
	    Hashtable variantTraceMapping = (Hashtable) variantLogMappingExcluded.get(1);
	    
		objectMapper.writeValue(pathToResult.resolve(Filename_mapping).toFile(), variantTraceMapping);
		Prom_without_Prom_Helper.exportSingleLog(logExcluded, pathToModel.resolve("Event_log_excluded_traces.xes").toString());
		
	}
	
	
	  public static List<String> readCSV(String csvFile) {
	        List<String> lines = new ArrayList<>();
	        
	        try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
	            String line;
	            while ((line = br.readLine()) != null) {
	                lines.add(line);
	            }
	        } catch (IOException e) {
	            e.printStackTrace();
	        }
	        
	        return lines;
	    }

}



