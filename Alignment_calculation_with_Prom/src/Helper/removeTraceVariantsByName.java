package Helper;

import java.util.ArrayList;
import java.util.Hashtable;
import java.util.Iterator;
import java.util.List;

import org.deckfour.xes.model.XAttributeMap;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import Helper.delete_traces_by_name;

public class removeTraceVariantsByName {

	
	  
	  public static XLog removeTraceVariantsByName(XLog log, List<String> traceVariantsToDelete) {
		  
			ArrayList variantLogMapping = logToLogOfTraceVariants.LogToLogOfVariants(log);
			
			XLog variantLog = (XLog) variantLogMapping.get(0);
			Hashtable variantMapping = (Hashtable) variantLogMapping.get(1);
			ArrayList traceNamesToDelete = new ArrayList();
			
			for (String traceVariant:traceVariantsToDelete){
				List<Integer> traceIndicies = (List<Integer>) variantMapping.get(traceVariant);
				for ( Integer traceIndex: traceIndicies) {
					String traceName = log.get(traceIndex-1).getAttributes().get("concept:name").toString();
					traceNamesToDelete.add(traceName);
				}
			
			
			}
			log = delete_traces_by_name.delete_traces_by_name(log,traceNamesToDelete);
		return log;
		  
	  }
}
