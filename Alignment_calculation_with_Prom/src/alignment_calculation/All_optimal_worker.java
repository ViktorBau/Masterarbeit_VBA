package alignment_calculation;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.time.Duration;
import java.time.Instant;

import org.deckfour.xes.model.XLog;

import Helper.HelperToNavigateDirectories;
import Prom_without_Prom.Prom_without_Prom_Helper;


public class All_optimal_worker {
	public static void main(String[] args) throws InterruptedException {
		
		
		// add name of Eventlog folder and path to it 
		String nameEventLog = ;
		Path pathToEventlog = Paths.get("PATH","PATH",nameEventLog);
		String nameOfEventLog = "Event_Log_only_complete.xes";
		ArrayList all_models = HelperToNavigateDirectories.getAllModelsFromDir(pathToEventlog);

		for (int i = 0; i < all_models.size(); i++) {
			String dirModel = (String) all_models.get(i);
			System.out.println("Starting with Model: "+ dirModel);
	
			Path pathToModel = pathToEventlog.resolve(dirModel);
			Path filePath = pathToModel.resolve("traces_excluded.csv");
			String filePathString = filePath.toString();
			
			
			try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePathString))) {
				  writer.write("");
	        } catch (IOException e) {
	            e.printStackTrace();
	        }
			
			String columnNames = "Trace name,Trace length,queued State,states,Alignemnts before Filter,Alignments after filter";
			Path filePathAlignmentStats = pathToModel.resolve("Alignment_amount_stats.csv");
			String filePathAlignmentStatsString = filePathAlignmentStats.toString();
			
			try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePathAlignmentStatsString))) {
				  writer.write(columnNames);
		          writer.newLine();
	        } catch (IOException e) {
	            e.printStackTrace();
	        }
			
		//tracking the delted traces  

			String createJob =  "sbatch --output=/vol/fob-vol3/mi20/baumanem/Slurm_output_all_optimal/"+nameEventLog +"/"+dirModel +"_run_" + 1 + ".out " + "--export=dirModel=" + dirModel+ ",path_to_event_log="+ pathToEventlog + " /vol/fob-vol3/mi20/baumanem/SLURM_jobs/calculate_all_optimal.sh"; 
			String resultCreateJob = executeCommand(createJob);
			int jobId = extractBatchNumber(resultCreateJob);
			Instant start =Instant.now();
			System.out.println("started Job: " + jobId);
			String JobStatus = "STARTING";
			boolean finished = false;
			int run = 1;
			//starting job and delteing traces that caused OOM event until the all optimal calcualtion manged to conclude
			while(!finished){
				String checkJobStauts = "scontrol show job " + jobId +" | grep JobState";
				String resultJobStatus = executeCommand(checkJobStauts);
				JobStatus = extractJobStatus(resultJobStatus);
				System.out.println(JobStatus);

				if(JobStatus.equals("FAILED") || JobStatus.equals("CANCELLED") ||   JobStatus.equals("OUT_OF_MEMORY")) {
					Instant end = Instant.now();
					System.out.println("run: " + run + "took: "+Duration.between(start, end).toMinutes() + "minutes");
					  String lastTrace = readCSV(pathToModel.resolve("last_trace.csv").toString()).get(0);
					  
					  try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePathString, true))) {
						  writer.write(lastTrace);
				          writer.newLine();
			      } catch (IOException e) {
			          e.printStackTrace();
			      }
			
					  List tracesToExcludeList = readCSV(pathToModel.resolve("traces_excluded.csv").toString());
					  String tracesToExclude = String.join("_",tracesToExcludeList);
					  System.out.println(tracesToExclude);
					  run++;
					  
					  
					  
					  
					  createJob =  "sbatch --output=/vol/fob-vol3/mi20/baumanem/Slurm_output_all_optimal/"+nameEventLog+"/"+dirModel +"_run_" +run+ ".out "+ "--export=dirModel=" + dirModel+ ",path_to_event_log="+ pathToEventlog + " /vol/fob-vol3/mi20/baumanem/SLURM_jobs/calculate_all_optimal.sh";
					  System.out.print(createJob);
					  
					  resultCreateJob = executeCommand(createJob);
					  start =Instant.now();
					  jobId = extractBatchNumber(resultCreateJob);
					  JobStatus = "PENDING";
					  System.out.println("started Job: " + jobId);
					  
					  
					//todo last_trace
				}
				else if (JobStatus.equals("COMPLETED")) {
					finished = true;
				}
				else {
					Thread.sleep(6000);
				}


			}
		}


	}


	public static String executeCommand(String command) {
		try {
			// Step 1: Create a ProcessBuilder instance and start the process
			ProcessBuilder processBuilder = new ProcessBuilder();
			processBuilder.command("bash", "-c", command);
			Process process = processBuilder.start();

			// Step 2: Capture the output stream of the process
			BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
			StringBuilder output = new StringBuilder();
			String line;

			while ((line = reader.readLine()) != null) {
				output.append(line).append("\n");
			}

			// Wait for the process to complete
			int exitCode = process.waitFor();
			if (exitCode != 0) {
				System.out.println("Command executed with errors");
			}

			return output.toString();

		} catch (IOException | InterruptedException e) {
			e.printStackTrace();
		}
		return "Error";
	}
	public static int extractBatchNumber(String inputString) {
		// Define the regex pattern to match the required format
		String pattern = "^Submitted batch job (\\d+)\n$";

		// Compile the pattern
		Pattern compiledPattern = Pattern.compile(pattern);

		// Match the pattern against the input string
		Matcher matcher = compiledPattern.matcher(inputString);

		// If the pattern is found, return the number
		if (matcher.matches()) {
			return Integer.parseInt(matcher.group(1));
		} else {
			// Throw an error if the input does not match the required format
			throw new IllegalArgumentException("Input string does not match the expected format 'Submitted batch ####'");
		}
	}
	public static String extractJobStatus(String inputString) {
		// Define the regex pattern to match the required format
		String pattern = "JobState=([^\\s]+).*";

		// Compile the pattern
		Pattern compiledPattern = Pattern.compile(pattern);

		// Match the pattern against the input string
		Matcher matcher = compiledPattern.matcher(inputString.trim());

		// If the pattern is found, return the number
		if (matcher.matches()) {
			return matcher.group(1);
		} else {
			// Throw an error if the input does not match the required format
			throw new IllegalArgumentException("Input string does not match the expected format 'Submitted batch ####'");
		}
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
