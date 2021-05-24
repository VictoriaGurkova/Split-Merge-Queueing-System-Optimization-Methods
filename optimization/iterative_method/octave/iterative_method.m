function [g,d]=iterative_method(n, nk, state_indices,p,q)
    d1=[];

    for i=1:length(state_indices)
        d1=[d1 1];
        state_indices(i)=state_indices(i)+1;
    end

    w=0;
    flag=true;

    % iterative loop
    while flag==true
        disp('Iteration ')
        w=w+1
        d=d1

        pd=[];
        qd=[];

        for i=1:n
            if in_list(i,state_indices)
                index=0;
                for j=1:length(state_indices)
                    if state_indices(j)==i
                        index=j;
                    end
                end
                pd=[pd;p(d(index),:,i)];
            else
                pd=[pd;p(1,:,i)];
            end
            qd=[qd;q(i)];
        end

        % solution of a system of linear equations (determination of weights)
        v=zeros(n,1);
        g=0;
        koef1=eye(n,n)-pd;
        koef=zeros(n,n);
        koef(:,1)=ones(n,1);
        koef(:,2:n)=koef1(:,1:n-1);
        x=koef\qd;
        g=x(1);
        v(1:n-1)=x(2:n);

        % solution improvement
        i=1;
        while i<=n
            if in_list(i,state_indices)
                kriter=zeros(1,nk);
                for k=1:nk
                    kriter(k)=q(k)+p(k,:,i)*v;
                end
                index=0;
                for j=1:length(state_indices)
                    if state_indices(j)==i
                        index=j;
                    end
                end
                dt=find(kriter==max(kriter));
                d1(index)=dt(1);
            end
            i=i+1;
        end

        disp('Solution at iteration')
        d1

        if all(d1==d)
            flag=false;
        end

    end
end

function b=in_list(i,state_indices)
    b=false;
    for index=1:length(state_indices)
        if state_indices(index)==i
            b=true;
        end
    end
end
