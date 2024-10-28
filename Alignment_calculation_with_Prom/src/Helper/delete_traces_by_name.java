package Helper;

import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.deckfour.xes.model.XAttributeMap;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class delete_traces_by_name {
	  public static XLog delete_traces_by_name(XLog log, List<String> traceNamesToDelete) {
	        List<XTrace> traces = log;
	        Iterator<XTrace> traceIterator = traces.iterator();

	        while (traceIterator.hasNext()) {
	            XTrace trace = traceIterator.next();
	            XAttributeMap attributes = trace.getAttributes();
	            String traceName = attributes.get("concept:name").toString();

	            if (traceNamesToDelete.contains(traceName)) {
	                traceIterator.remove();
	            }
	        }

	        return log;
	    }

}
