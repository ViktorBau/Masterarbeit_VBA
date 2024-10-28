package Helper;

import java.io.File;
import java.io.FileOutputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import org.deckfour.xes.factory.XFactory;
import org.deckfour.xes.factory.XFactoryRegistry;
import org.deckfour.xes.in.XParser;
import org.deckfour.xes.in.XesXmlParser;
import org.deckfour.xes.model.XLog;
import org.deckfour.xes.model.XTrace;
import org.deckfour.xes.model.impl.XLogImpl;
import org.deckfour.xes.out.XesXmlSerializer;

public class sort_event_log_by_trace_length {
	
	public static  XLog sortXLogByTraceLength(XLog log){
	
		
	List<XTrace> traces = new ArrayList<>(log);
	
	Collections.sort(traces, new Comparator<XTrace>() {
        @Override
        public int compare(XTrace trace1, XTrace trace2) {
            return Integer.compare(trace1.size(), trace2.size());
        }
    });

    // Step 4: Create a New XLog and Add Sorted Traces
	XLog sortedLog = new XLogImpl(log.getAttributes());
    for (XTrace trace : traces) {
    	sortedLog.add(trace);
    }
    
    return sortedLog;
	}
}
