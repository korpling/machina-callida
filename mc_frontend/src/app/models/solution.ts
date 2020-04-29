import {SolutionElement} from 'src/app/models/solutionElement';

export class Solution {
    public target: SolutionElement;
    public value: SolutionElement;

    constructor(init?: Partial<Solution>) {
        Object.assign(this, init);
    }
}
