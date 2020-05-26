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
 * Collection of texts.
 */
export interface Corpus { 
    /**
     * Author of the texts in the corpus.
     */
    author?: string;
    /**
     * Unique identifier for the corpus.
     */
    cid?: number;
    /**
     * First level for citing the corpus.
     */
    citation_level_1?: string;
    /**
     * Second level for citing the corpus.
     */
    citation_level_2?: string;
    /**
     * Third level for citing the corpus.
     */
    citation_level_3?: string;
    /**
     * CTS base URN for referencing the corpus.
     */
    source_urn: string;
    /**
     * Corpus title.
     */
    title?: string;
}

