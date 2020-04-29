import {async, ComponentFixture, TestBed} from '@angular/core/testing';
import {SemanticsPage} from './semantics.page';
import {RouterModule} from '@angular/router';
import {HttpClientModule, HttpErrorResponse} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {of} from 'rxjs';
import {APP_BASE_HREF} from '@angular/common';
import Spy = jasmine.Spy;
import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';

describe('SemanticsPage', () => {
    let semanticsPage: SemanticsPage;
    let fixture: ComponentFixture<SemanticsPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [SemanticsPage],
            imports: [
                FormsModule,
                HttpClientModule,
                IonicStorageModule.forRoot(),
                MatSlideToggleModule,
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        }).compileComponents().then();
        fixture = TestBed.createComponent(SemanticsPage);
        semanticsPage = fixture.componentInstance;
        fixture.detectChanges();
    }));

    it('should create', () => {
        expect(semanticsPage).toBeTruthy();
        expect(semanticsPage.getWhiteSpace()).toBe(' ');
    });

    it('should get similar contexts', (done) => {
        const requestSpy: Spy = spyOn(semanticsPage.helperService, 'makePostRequest').and.callFake(() => Promise.reject());
        semanticsPage.getSimilarContexts().then(() => {
        }, () => {
            expect(semanticsPage.similarContexts.length).toBe(0);
            requestSpy.and.returnValue(Promise.resolve([['a']]));
            semanticsPage.highlightRegex = 'a';
            semanticsPage.getSimilarContexts().then(() => {
                expect(semanticsPage.similarContexts.length).toBe(1);
                expect(semanticsPage.highlightSet.size).toBe(1);
                done();
            });
        });
    });

    it('should be initialized', (done) => {
        const updateSpy: Spy = spyOn(semanticsPage, 'updateVectorNetwork').and.returnValue(Promise.resolve());
        const contextSpy: Spy = spyOn(semanticsPage, 'getSimilarContexts').and.returnValue(Promise.resolve());
        semanticsPage.activatedRoute.queryParams = of({minCount: '0'});
        semanticsPage.ngAfterViewInit().then(() => {
            expect(semanticsPage.minCount).toBe(0);
            semanticsPage.activatedRoute.queryParams = of({
                searchRegex: 'a',
                highlightRegex: 'b',
                nearestNeighborCount: '0'
            });
            semanticsPage.ngAfterViewInit().then(() => {
                expect(updateSpy).toHaveBeenCalledTimes(1);
                semanticsPage.isKWICview = true;
                semanticsPage.ngAfterViewInit().then(() => {
                    expect(contextSpy).toHaveBeenCalledTimes(1);
                    done();
                });
            });
        });
    });

    it('should update the vector network', (done) => {
        const requestSpy: Spy = spyOn(semanticsPage.helperService, 'makeGetRequest').and.returnValue(Promise.resolve('a'));
        const toastSpy: Spy = spyOn(semanticsPage.helperService, 'showToast').and.returnValue(Promise.resolve());
        semanticsPage.searchRegex = 'a';
        semanticsPage.updateVectorNetwork().then(() => {
            expect(semanticsPage.kwicGraphs).toBeTruthy();
            requestSpy.and.callFake(() => Promise.reject(new HttpErrorResponse({status: 422})));
            semanticsPage.updateVectorNetwork().then(() => {
            }, () => {
                expect(toastSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });
});
