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
 * Relevant parameters for creating a Keyword In Context view.
 */
export interface KwicForm { 
    /**
     * Search queries that were used to build the exercise.
     */
    search_values: string;
    /**
     * CTS URN for the text passage from which the KWIC view should be generated.
     */
    urn: string;
    /**
     * Number of tokens that should be given as context on the left side of a target.
     */
    ctx_left: number;
    /**
     * Number of tokens that should be given as context on the right side of a target.
     */
    ctx_right: number;
}

