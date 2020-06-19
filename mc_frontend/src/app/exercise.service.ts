/* tslint:disable:no-string-literal */
import {Injectable} from '@angular/core';
import configMC from '../configMC';
import {HelperService} from './helper.service';
import {ExercisePart} from './models/exercisePart';
import {Options} from './models/h5p-standalone.class';
import {EventMC} from './models/enum';

declare var H5PStandalone: any;

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
            i => this.currentExerciseParts[i].startIndex <= this.currentExerciseIndex &&
                (!this.currentExerciseParts[i + 1] || this.currentExerciseParts[i + 1].startIndex > this.currentExerciseIndex));
        const cepi: number = this.currentExercisePartIndex;
        this.currentExerciseName = this.currentExercisePartIndex ?
            this.currentExerciseParts[cepi].exercises[this.currentExerciseIndex - this.currentExerciseParts[cepi].startIndex] :
            '';
    }

    public currentExerciseName: string;
    public currentExercisePartIndex: number;
    public currentExerciseParts: ExercisePart[];
    public excludeOOV = false;
    public fillBlanksString = 'fill_blanks';
    public h5pContainerString = '.h5p-container';
    public h5pIframeString = '.h5p-iframe';
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

    createH5Pstandalone(el: HTMLElement, h5pLocation: string): Promise<void> {
        return new H5PStandalone.H5P(el, h5pLocation);
    }

    initH5P(exerciseTypePath: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const el: HTMLDivElement = document.querySelector(this.h5pContainerString);
            const h5pLocation = 'assets/h5p/' + exerciseTypePath;
            const options: Options = {
                frameCss: 'assets/h5p-standalone-master/dist/styles/h5p.css',
                frameJs: 'assets/h5p-standalone-master/dist/frame.bundle.js',
                preventH5PInit: false
            };
            this.createH5Pstandalone(el, h5pLocation).then(() => {
                // dirty hack to wait for all the H5P elements being added to the DOM
                setTimeout(() => {
                    this.helperService.events.trigger(EventMC.h5pCreated, {data: {library: exerciseTypePath}});
                    return resolve();
                }, 150);
            });
        });
    }

    setH5Purl(url: string): void {
        // this has to be LocalStorage because the H5P javascript cannot easily access the Ionic Storage
        window.localStorage.setItem(configMC.localStorageKeyH5P, url);
    }
}
