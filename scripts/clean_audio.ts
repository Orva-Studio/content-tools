#!/usr/bin/env bun

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { Command } from 'commander';
import FormData from 'form-data';

// Environment variables
const API_KEY = process.env.AUPHONIC_API_KEY;
const BASE_URL = 'https://auphonic.com/api';

// Constants
const MAX_WAIT_TIME = 300; // 5 minutes
const STATUS_CHECK_INTERVAL = 15000; // 15 seconds
const INITIAL_WAIT_TIME = 5000; // 5 seconds
const PRODUCTION_START_DELAY = 2000; // 2 seconds

// Interfaces
interface ApiResponse<T = any> {
  data?: T;
  status?: number;
  [key: string]: any;
}

interface Preset {
  uuid: string;
  preset_name: string;
}

interface Production {
  uuid: string;
  title: string;
}

interface ProductionStatus {
  status: number;
  status_string: string;
  error_summary?: string;
  error_message?: string;
  warning_message?: string;
}

interface OutputFile {
  download_url: string;
  filename: string;
}

interface ProductionDetails {
  output_files: OutputFile[];
}

interface ProcessingResult {
  success: boolean;
  error?: string;
  productionUuid?: string;
}

interface DownloadResult {
  success: boolean;
  error?: string;
  downloadedFiles?: string[];
}

// Error handling
function exitWithError(message: string, statusCode?: number, responseText?: string): never {
  console.error(`ERROR: ${message}`);
  
  if (statusCode && responseText) {
    console.error('Full response content:');
    console.error(statusCode, responseText);
  }
  
  process.exit(1);
}

// File validation functions
function checkFileExists(filePath: string): ProcessingResult {
  try {
    const stats = fs.statSync(filePath);
    const isFile = stats.isFile();
    
    if (!isFile) {
      return {
        success: false,
        error: `Path is not a file: ${filePath}`
      };
    }
    
    // Check if file is readable
    fs.accessSync(filePath, fs.constants.R_OK);
    
    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return {
      success: false,
      error: `Audio file validation failed: ${errorMessage}`
    };
  }
}

function ensureDirectoryExists(dirPath: string): ProcessingResult {
  try {
    fs.mkdirSync(dirPath, { recursive: true });
    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return {
      success: false,
      error: `Failed to create directory: ${errorMessage}`
    };
  }
}

// API functions
async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    ...options.headers,
  };
  
  return fetch(url, {
    ...options,
    headers,
  });
}

async function findPresetUuid(presetName: string): Promise<string | null> {
  try {
    const response = await fetchWithAuth(`${BASE_URL}/presets.json?minimal_data=1`);
    
    if (!response.ok) {
      exitWithError('Failed to fetch presets', response.status, await response.text());
    }
    
    const data: ApiResponse<Preset[]> = await response.json();
    const presets = data.data || [];
    
    const matchingPreset = presets.find(preset => preset.preset_name === presetName);
    
    if (!matchingPreset) {
      console.log('Preset not found. Available presets:');
      presets.forEach(preset => {
        console.log(`- ${preset.preset_name}`);
      });
      return null;
    }
    
    return matchingPreset.uuid;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    exitWithError(`Failed to find preset: ${errorMessage}`);
  }
}

async function uploadFileAndCreateProduction(
  filePath: string, 
  presetUuid: string | null
): Promise<string> {
  try {
    const form = new FormData();
    const fileStream = fs.createReadStream(filePath);
    const fileName = path.basename(filePath);
    
    form.append('input_file', fileStream);
    form.append('title', `Processed ${fileName}`);
    
    if (presetUuid) {
      form.append('preset', presetUuid);
      console.log(`Using preset UUID: ${presetUuid}`);
    }
    
    const response = await fetchWithAuth(`${BASE_URL}/simple/productions.json`, {
      method: 'POST',
      body: form,
    });
    
    if (!response.ok) {
      exitWithError('File upload and production creation failed', response.status, await response.text());
    }
    
    const data: ApiResponse<Production> = await response.json();
    const productionUuid = data.data?.uuid;
    
    if (!productionUuid) {
      exitWithError('Failed to get valid production UUID after upload');
    }
    
    return productionUuid;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    exitWithError(`Could not upload file: ${errorMessage}`);
  }
}

async function startProduction(productionUuid: string): Promise<void> {
  // Wait before starting production
  await new Promise(resolve => setTimeout(resolve, PRODUCTION_START_DELAY));
  
  console.log('Starting production...');
  
  try {
    const response = await fetchWithAuth(`${BASE_URL}/production/${productionUuid}/start.json`, {
      method: 'POST',
    });
    
    if (response.ok) {
      console.log('Production started successfully');
      return;
    }
    
    console.log(`Start response status: ${response.status}`);
    console.log(`Start response: ${await response.text()}`);
    
    // Check current status if start failed
    const statusResponse = await fetchWithAuth(`${BASE_URL}/production/${productionUuid}/status.json`);
    
    if (statusResponse.ok) {
      const statusData: ApiResponse<ProductionStatus> = await statusResponse.json();
      const currentStatus = statusData.data?.status;
      
      // Status codes: 1=Waiting, 2=Processing, 3=Done
      if (currentStatus && [1, 2, 3].includes(currentStatus)) {
        console.log('Production appears to be already started or completed');
        return;
      }
    }
    
    exitWithError('Failed to start production');
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    exitWithError(`Failed to start production: ${errorMessage}`);
  }
}

async function waitForProcessingComplete(productionUuid: string): Promise<void> {
  const startTime = Date.now();
  
  // Initial wait before checking status
  await new Promise(resolve => setTimeout(resolve, INITIAL_WAIT_TIME));
  
  while (true) {
    try {
      const response = await fetchWithAuth(`${BASE_URL}/production/${productionUuid}/status.json`);
      
      if (!response.ok) {
        exitWithError('Failed to get production status', response.status, await response.text());
      }
      
      const data: ApiResponse<ProductionStatus> = await response.json();
      const statusInfo = data.data;
      
      if (!statusInfo) {
        exitWithError('Failed to get status response data');
      }
      
      const { status, status_string: statusString } = statusInfo;
      console.log(`Status: ${statusString} (code: ${status})`);
      
      if (status === 3) {
        console.log('Processing complete!');
        break;
      }
      
      // Status codes: 1=Waiting, 2=Processing, 4=Audio Processing
      const isProcessingStatus = [1, 2, 4].includes(status);
      
      if (isProcessingStatus) {
        // Continue waiting
      } else if (status === 5) {
        // Error status
        await handleProcessingError(productionUuid);
        process.exit(1);
      } else {
        console.log(`Unknown status code: ${status}. Continuing to wait...`);
      }
      
      // Check for timeout
      const elapsedTime = Date.now() - startTime;
      const hasTimedOut = elapsedTime > MAX_WAIT_TIME * 1000;
      
      if (hasTimedOut) {
        console.log(`Processing timed out after ${MAX_WAIT_TIME} seconds`);
        console.log(`You can check the status manually at: https://auphonic.com/engine/status/${productionUuid}`);
        process.exit(1);
      }
      
      await new Promise(resolve => setTimeout(resolve, STATUS_CHECK_INTERVAL));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      exitWithError(`Failed to check production status: ${errorMessage}`);
    }
  }
}

async function handleProcessingError(productionUuid: string): Promise<void> {
  console.log('Processing failed! Getting detailed error information...');
  
  try {
    const response = await fetchWithAuth(`${BASE_URL}/production/${productionUuid}.json`);
    
    if (!response.ok) {
      exitWithError('Failed to fetch production details after processing failure', response.status, await response.text());
    }
    
    const responseText = await response.text();
    console.log('Full production details below for debugging:');
    console.log(responseText);
    
    try {
      const details: ApiResponse<ProductionStatus> = JSON.parse(responseText);
      const data = details.data;
      
      if (data) {
        console.log(`Error Summary: ${data.error_summary || 'No summary available'}`);
        console.log(`Error Message: ${data.error_message || 'No detailed message available'}`);
        console.log(`Warning Message: ${data.warning_message || 'No warnings'}`);
      }
    } catch (parseError) {
      console.log(`Could not parse details JSON: ${parseError}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.log(`Failed to get error details: ${errorMessage}`);
  }
}

async function downloadResultFiles(productionUuid: string, outputDir: string): Promise<DownloadResult> {
  try {
    const response = await fetchWithAuth(`${BASE_URL}/production/${productionUuid}.json`);
    
    if (!response.ok) {
      return {
        success: false,
        error: 'Failed to fetch output files for completed production'
      };
    }
    
    const data: ApiResponse<ProductionDetails> = await response.json();
    const outputFiles = data.data?.output_files || [];
    const downloadedFiles: string[] = [];
    
    for (const file of outputFiles) {
      const { download_url: downloadUrl, filename } = file;
      
      if (downloadUrl && filename) {
        console.log('Downloading:', filename);
        
        const fileResponse = await fetchWithAuth(downloadUrl);
        
        if (!fileResponse.ok) {
          return {
            success: false,
            error: `Download of ${filename} failed`
          };
        }
        
        const outputPath = path.join(outputDir, filename);
        const buffer = Buffer.from(await fileResponse.arrayBuffer());
        
        fs.writeFileSync(outputPath, buffer);
        console.log('Saved to:', outputPath);
        downloadedFiles.push(outputPath);
      }
    }
    
    return {
      success: true,
      downloadedFiles
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return {
      success: false,
      error: `Failed to download result files: ${errorMessage}`
    };
  }
}

// Main function
async function main(): Promise<void> {
  const program = new Command();
  
  program
    .name('clean-audio')
    .description('Upload audio file to Auphonic for processing')
    .argument('<file_path>', 'Path to the audio file to process')
    .option('-p, --preset <name>', 'Preset name to use', 'Usual-2')
    .option('-o, --output-dir <path>', 'Output directory for processed files', '~/Downloads/auphonic_results')
    .parse();
  
  const options = program.opts();
  const [filePath] = program.args;
  
  // Validate environment variables
  if (!API_KEY) {
    exitWithError('AUPHONIC_API_KEY environment variable is required');
  }
  
  // Expand paths
  const expandedFilePath = filePath.startsWith('~') 
    ? path.join(os.homedir(), filePath.slice(1))
    : path.resolve(filePath);
    
  const expandedOutputDir = options.outputDir.startsWith('~')
    ? path.join(os.homedir(), options.outputDir.slice(1))
    : path.resolve(options.outputDir);
  
  // Validate input file
  const fileValidation = checkFileExists(expandedFilePath);
  if (!fileValidation.success) {
    exitWithError(fileValidation.error!);
  }
  
  // Ensure output directory exists
  const dirValidation = ensureDirectoryExists(expandedOutputDir);
  if (!dirValidation.success) {
    exitWithError(dirValidation.error!);
  }
  
  try {
    // Find preset UUID
    console.log('Looking up preset:', options.preset);
    const presetUuid = await findPresetUuid(options.preset);
    
    if (!presetUuid) {
      process.exit(1);
    }
    
    // Upload file and create production
    console.log(`Uploading file: ${expandedFilePath}`);
    const productionUuid = await uploadFileAndCreateProduction(expandedFilePath, presetUuid);
    
    console.log('Production created:', productionUuid);
    console.log('Monitor at: https://auphonic.com/engine/status/' + productionUuid);
    
    // Start production
    await startProduction(productionUuid);
    
    // Wait for processing to complete
    await waitForProcessingComplete(productionUuid);
    
    // Download result files
    const downloadResult = await downloadResultFiles(productionUuid, expandedOutputDir);
    
    if (!downloadResult.success) {
      exitWithError(downloadResult.error!);
    }
    
    console.log('Processing completed successfully!');
    
    if (downloadResult.downloadedFiles && downloadResult.downloadedFiles.length > 0) {
      console.log('Downloaded files:');
      downloadResult.downloadedFiles.forEach(file => console.log(`- ${file}`));
    }
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    exitWithError(`Unexpected error: ${errorMessage}`);
  }
}

// Run the script
if (require.main === module) {
  main().catch(error => {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    exitWithError(`Unhandled error: ${errorMessage}`);
  });
}

export { main };
