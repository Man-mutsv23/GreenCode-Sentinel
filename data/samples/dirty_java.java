package data.samples;

import java.util.*;

/**
 * GreenCode Sentinel - Dirty Test Case
 * Contains intentional carbon-heavy patterns: O(n^3) loops, memory leaks, and N+1 query patterns.
 */
public class dirty_java {

    public static void main(String[] args) {
        List<Integer> data = new ArrayList<>();
        for (int i = 0; i < 50; i++) data.add(i);
        
        runInefficientAnalysis(data);
    }

    /**
     * ISSUE: Triple nested loop - O(n^3) complexity.
     * Wastes massive CPU cycles for large inputs.
     */
    public static void runInefficientAnalysis(List<Integer> data) {
        List<String> results = new ArrayList<>();
        
        for (int i = 0; i < data.size(); i++) {
            for (int j = 0; j < data.size(); j++) {
                for (int k = 0; k < data.size(); k++) {
                    if (data.get(i) + data.get(j) == data.get(k)) {
                        // ISSUE: String concatenation in a loop
                        // Creates a new String object every time, causing GC pressure.
                        String match = "Match: " + i + "," + j + "," + k;
                        results.add(match);
                    }
                }
            }
        }
    }

    /**
     * ISSUE: Memory Inefficiency & Redundant API Simulation.
     * Making "network calls" in a loop without batching.
     */
    public void processUsers(List<String> userIds) {
        List<Object> cachedData = new ArrayList<>();
        
        for (String id : userIds) {
            // ISSUE: N+1 Query Pattern
            // Simulating fetching details one by one instead of a single JOIN/Batch.
            Object user = mockApiCall("/users/" + id);
            Object profile = mockApiCall("/profiles/" + id);
            
            // ISSUE: Creating unnecessary heavy copies
            List<Object> temporaryCopy = new ArrayList<>(cachedData);
            temporaryCopy.add(user);
            cachedData = temporaryCopy;
        }
    }

    private Object mockApiCall(String url) {
        try { Thread.sleep(50); } catch (Exception e) {} // Simulate latency
        return new Object();
    }
}