package alignment_calculation;

import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Hashtable;
import java.util.TreeSet;
import java.util.concurrent.Future;

import org.deckfour.xes.classification.XEventClass;
import org.deckfour.xes.classification.XEventClassifier;
import org.deckfour.xes.info.impl.XLogInfoImpl;
import org.deckfour.xes.model.XLog;
import org.processmining.framework.plugin.GlobalContext;
import org.processmining.framework.plugin.PluginContext;
import org.processmining.framework.plugin.impl.AbstractPluginContext;
import org.processmining.models.graphbased.directed.petrinet.Petrinet;
import org.processmining.models.graphbased.directed.petrinet.PetrinetGraph;
import org.processmining.models.graphbased.directed.petrinet.elements.Place;
import org.processmining.models.semantics.petrinet.Marking;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.algorithms.PlanningBasedAlignment;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.models.PlanningBasedReplayResult;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.parameters.PlanningBasedAlignmentParameters;
import org.processmining.planningbasedalignment.plugins.planningbasedalignment.ui.PlanningBasedAlignmentConfiguration;
import org.processmining.plugins.DataConformance.Alignment;
import org.processmining.plugins.connectionfactories.logpetrinet.TransEvClassMapping;

import com.fasterxml.jackson.databind.ObjectMapper;

import Helper.HelperToNavigateDirectories;
import planingBasedAlignments.planningBasedAlignment_overwrite;
import planingBasedAlignments.PlanningBasedAlignmentConfiguration_overwrite_VBA;
import planingBasedAlignments.UIPluginContext;
import Prom_without_Prom.PluginContextFactory;
import Prom_without_Prom.Prom_without_Prom_Helper;
import Helper.logToLogOfTraceVariants;
import nl.tue.alignment.TraceReplayTask;

public class Planning_based_one_optimal {

	public static <E> void main(String[] args) throws Exception {
	
		//Path pathToEventlog = Paths.get("/vol","fob-vol3","mi20","baumanem","alignments","BPI_2012_remove_longest_traces");
		Path pathToEventlog = Paths.get("ADD PATH TO EVENTLOG FOLDER");
	
		String nameOfEventLog = "Event_log_excluded_traces.xes";
	//add path to python max 2.7 
	String pythonInterpreter = "C:\\Python32\\python.exe";
	//String pythonInterpreter = "/usr/bin/python";
	String Filename_alignment = "planning_based_alignment.json";
	String Filename_mapping = "planning_based_alignment_mapping_variant_traces.json";
	
	ArrayList all_models = HelperToNavigateDirectories.getAllModelsFromDir(pathToEventlog);
	
	for (int i = 0; i < all_models.size(); i++) {
		String dirModel = (String) all_models.get(i);
	System.out.println("Starting on" + dirModel);
	Path pathToModel = pathToEventlog.resolve(dirModel);
	Path pathToResult = pathToModel.resolve("PROM_alignment_results");
	 if (!Files.exists(pathToResult)) {
		 Files.createDirectories(pathToResult);
	 }
	 if (!Files.exists(pathToResult.resolve(Filename_alignment))) {
		 
	 
	 
	
	

	
	

	XLog logOrginal = Prom_without_Prom_Helper.readSingleLog(pathToModel.resolve(nameOfEventLog).toFile());
	ArrayList variantLog = logToLogOfTraceVariants.LogToLogOfVariants(logOrginal);
	XLog log = (XLog) variantLog.get(0);
	Hashtable mappingVaraintsTraces = (Hashtable) variantLog.get(1);
	
	Object[] petri= Prom_without_Prom_Helper.importFromFile(pathToModel.resolve("Petri_net.pnml").toFile(), "Petri_net");
	Petrinet net = (Petrinet) petri[0];
	
	
	XEventClass dummyEvClass = new XEventClass("DUMMY", 99999);
	XEventClassifier eventClassifier = XLogInfoImpl.STANDARD_CLASSIFIER;
	TransEvClassMapping mapping = Prom_without_Prom_Helper.constructMapping(net, log, dummyEvClass,
			eventClassifier, true);
	
	
	
	Hashtable<String, Hashtable<String, Object>> alignmentResults = Planning_based_one_optimal(pathToResult, pythonInterpreter, log, net, mapping);
	


	ObjectMapper objectMapper = new ObjectMapper();
	objectMapper.writeValue(pathToResult.resolve(Filename_alignment).toFile(), alignmentResults);
	objectMapper.writeValue(pathToResult.resolve(Filename_mapping).toFile(), mappingVaraintsTraces);
	 }
	 else {
		 System.out.println(dirModel+ "is skipped, because it already exists");
	 }
	}
	}
	

	public static Hashtable<String, Hashtable<String, Object>> Planning_based_one_optimal (Path pathToResult, String pythonInterpreter, XLog log, Petrinet net, TransEvClassMapping mapping) throws IOException, InterruptedException, URISyntaxException{
		PlanningBasedAlignmentConfiguration_overwrite_VBA configurationUI = new PlanningBasedAlignmentConfiguration_overwrite_VBA();
		PlanningBasedAlignmentParameters parameters = configurationUI.getParameters_no_Prom(log, net , Prom_without_Prom_Helper.getInitialMarking(net), Prom_without_Prom_Helper.getFinalMarking(net), mapping);
		
		PluginContextFactory factory = new PluginContextFactory();
		GlobalContext contextGlobal = (GlobalContext)factory.getContext();
		UIPluginContext context = new UIPluginContext(contextGlobal, "Dummy");
		
		
		planningBasedAlignment_overwrite alignmentProcess = new planningBasedAlignment_overwrite();
		alignmentProcess.buildPlannerInput_overwrite(pathToResult.toFile(), context, log, net, parameters);
		alignmentProcess.invokePlanner(pythonInterpreter, context, parameters);			
		PlanningBasedReplayResult result = alignmentProcess.parsePlannerOutput( log, net, parameters);
		
		
		Hashtable<String, Hashtable<String, Object>> alignmentResults = new Hashtable<>();
		
		
		Collection<Alignment> alignments =  result.getAlignments();
		for (Alignment trace:alignments){
			Hashtable<String, Object> traceResult = new Hashtable<>();
			traceResult.put("stepLabels", trace.getStepLabels());
			traceResult.put("stepTypes", trace.getStepTypes().toString());
			alignmentResults.put(trace.getTraceName(), traceResult);
		}
		return alignmentResults;
		
	}
}
