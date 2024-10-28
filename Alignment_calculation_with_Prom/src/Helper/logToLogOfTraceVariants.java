package Helper;

import java.util.Hashtable;
import java.util.List;
import java.util.Map;
import java.util.ArrayList;

import org.deckfour.xes.extension.std.XConceptExtension;
import org.deckfour.xes.model.XEvent;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.deckfour.xes.model.impl.XLogImpl;



public class logToLogOfTraceVariants {
	
	public static  ArrayList LogToLogOfVariants(XLog log){
		  // Map to store unique trace variants
		Hashtable<String, XTrace> uniqueTraces = new Hashtable<>();
		Hashtable<String, Hashtable<String, Object>> mappingVariantToTraces = new Hashtable<>();
		ArrayList orderOfVariants = new ArrayList(); 
        int index = 1;
        // Iterate through traces and keep only unique variants
        for (XTrace trace : log) {
            StringBuilder variantBuilder = new StringBuilder();
            for (XEvent event : trace) {
                variantBuilder.append(event.getAttributes().get("concept:name").toString());
                variantBuilder.append(",");
            }
            String variant = variantBuilder.toString();
            if (!uniqueTraces.containsKey(variant)) {
            	
                uniqueTraces.put(variant, trace);
                
              
                
                Hashtable<String, Object> variantTraces = new Hashtable<String, Object>();
                ArrayList indiciesOfTraces = new ArrayList();
                indiciesOfTraces.add(index);
                variantTraces.put("indices of traces", indiciesOfTraces);
                variantTraces.put("name of first Trace", trace.getAttributes().get("concept:name").toString());
                
                
                mappingVariantToTraces.put(variant, variantTraces);
                orderOfVariants.add(variant);
            }
            else {
            	((ArrayList) mappingVariantToTraces.get(variant).get("indices of traces")).add(index);
            }
            index++;
        }

        // Create a new log with unique traces
        XLog uniqueLog = new XLogImpl(log.getAttributes());
        Hashtable indiciesOfTraces = new Hashtable();
        for (int i = 0; i < orderOfVariants.size(); i++) {
        	String trace = (String) orderOfVariants.get(i);
            uniqueLog.add(uniqueTraces.get(trace));
            indiciesOfTraces.put(mappingVariantToTraces.get(trace).get("name of first Trace"),mappingVariantToTraces.get(trace).get("indices of traces"));
        }
        
        ArrayList result = new ArrayList();
        result.add(uniqueLog);
        result.add(indiciesOfTraces);
		return result;
		
	}

}
