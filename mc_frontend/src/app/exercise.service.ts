/* tslint:disable:no-string-literal */
import {Injectable} from '@angular/core';
import configMC from '../configMC';
import {HelperService} from './helper.service';
import {ExercisePart} from './models/exercisePart';

@Injectable({
    providedIn: 'root'
})
export class ExerciseService {
    // tslint:disable-next-line:variable-name
    private _currentExerciseIndex: number;
    get currentExerciseIndex(): number {
        return this._currentExerciseIndex;
    }

    set currentExerciseIndex(value: number) {
        this._currentExerciseIndex = value;
        this.currentExercisePartIndex = [...Array(this.currentExerciseParts.length).keys()].find(
            i => this.currentExerciseParts[i].startIndex <= this.currentExerciseIndex && (!this.currentExerciseParts[i + 1]
                || this.currentExerciseParts[i + 1].startIndex > this.currentExerciseIndex));
        const cepi: number = this.currentExercisePartIndex;
        this.currentExerciseName = this.currentExercisePartIndex ?
            this.currentExerciseParts[cepi].exercises[this.currentExerciseIndex - this.currentExerciseParts[cepi].startIndex] : '';
    }

    public currentExerciseName: string;
    public currentExercisePartIndex: number;
    public currentExerciseParts: ExercisePart[];
    public excludeOOV = false;
    public fillBlanksString = 'fill_blanks';
    public h5pContainerString = '.h5p-container';
    public h5pIframeString = '#h5p-iframe-1';
    public kwicGraphs: string;
    public vocListString = 'voc_list';

    constructor(public helperService: HelperService) {
    }

    createGuid(): string {
        function s4(): string {
            return Math.floor((1 + Math.random()) * 0x10000)
                .toString(16)
                .substring(1);
        }

        return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
    }

    initH5P(exerciseTypePath: string): Promise<void> {
        return new Promise(resolve => {
            // dirty hack to get H5P going without explicit button click on the new page
            setTimeout(() => {
                // noinspection TypeScriptValidateJSTypes
                this.helperService.getH5P().jQuery(this.h5pContainerString).empty().h5p({
                    frameJs: 'assets/dist/js/h5p-standalone-frame.min.js',
                    frameCss: 'assets/dist/styles/h5p.css',
                    h5pContent: 'assets/h5p/' + exerciseTypePath
                });
                return resolve();
            }, 50);
        });
    }

    setH5Purl(url: string): void {
        // this has to be LocalStorage because the H5P javascript cannot easily access the Ionic Storage
        window.localStorage.setItem(configMC.localStorageKeyH5P, url);
    }
}
