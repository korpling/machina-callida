/**
 * Machina Callida Backend REST API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */


/**
 * Relevant parameters for finding sentences that are similar to a target word.
 */
export interface VectorNetworkForm { 
    /**
     * Regular expression for a textual search.
     */
    search_regex: string;
    /**
     * Number of nearest neighbors that should be considered for each target node in a graph analysis.
     */
    nearest_neighbor_count?: number;
}

