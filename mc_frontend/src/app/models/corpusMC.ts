/* tslint:disable:variable-name */
import {Citation} from 'src/app/models/citation';
import {Corpus} from '../../../openapi';

export interface CorpusMC extends Corpus {
    citations?: { [label: string]: Citation; };
}
